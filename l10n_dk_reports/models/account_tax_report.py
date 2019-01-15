from odoo import models, fields, api, _
import logging
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

class ReportTax(models.AbstractModel):
    _name = 'report.l10n_dk_reports.l10n_dk_tax_report'


    @api.model
    def get_report_values(self, docids, data=None):
        if not data.get('form'):
            raise UserError(_("Form content is missing, this report cannot be printed."))
        
        # data are values from the wizard form, lines are whatever you return from get_lines()
        return {
            'company': self.env.user.company_id,
            'data': data['form'],
            'lines': self.get_lines(data.get('form')),
        }

    @api.model
    def get_lines(self, options):
        lines = {}

        self.get_moms(options, lines)
        self.get_fradrag(options, lines)
        self.get_supp_opl(options, lines)

        return lines

    def get_moms(self, options, lines):
        # Line 1 - Salgsmoms (udgaende moms)
        tax_tag = self.env.ref('l10n_dk.tag_tax_sale')
        lines['salgsmoms'] = self.get_aml_tax(options, tax_tag.id)

        tax_tag = self.env.ref('l10n_dk.tag_tax_quarter_sale')
        lines['salgsmoms'] += self.get_aml_tax(options, tax_tag.id)

        tax_tag = self.env.ref('l10n_dk.tag_tax_half_sale')
        lines['salgsmoms'] += self.get_aml_tax(options, tax_tag.id)

        # Line 2 - Moms af varekob i udlandet (bade eu og tredjelande)
        tax_tag = self.env.ref('l10n_dk.tag_tax_eu_purchase_in')
        lines['moms_vare_eu_in'] = self.get_aml_tax(options, tax_tag.id)

        # Line 3 - Moms af ydelseskob i udlandet med omvendt betalingspligt
        tax_tag = self.env.ref('l10n_dk.tag_tax_eu_purchase_service_in')
        lines['moms_ydelse_eu'] = self.get_aml_tax(options, tax_tag.id)
    
    def get_fradrag(self, options, lines):
        # Line 1 - Kobsmoms (indgaende moms)
        tax_tag = self.env.ref('l10n_dk.tag_tax_purchase')
        lines['kobsmoms'] = self.get_aml_tax(options, tax_tag.id)

        tax_tag = self.env.ref('l10n_dk.tag_tax_quarter_purchase')
        lines['kobsmoms'] += self.get_aml_tax(options, tax_tag.id)

        tax_tag = self.env.ref('l10n_dk.tag_tax_half_purchase')
        lines['kobsmoms'] += self.get_aml_tax(options, tax_tag.id)

        # Reverse Charge
        tax_tag = self.env.ref('l10n_dk.tag_tax_eu_purchase_rc')
        lines['kobsmoms'] += self.get_aml_tax(options, tax_tag.id)
        tax_tag = self.env.ref('l10n_dk.tag_tax_eu_purchase_service_rc')
        lines['kobsmoms'] += self.get_aml_tax(options, tax_tag.id)
        # Line 2 - Olie- og flaskegasafgift
        account_tag = self.env.ref('l10n_dk.tag_tax_olie_gas')
        lines['olie_gas_afgift'] = self.get_aml_account(options, account_tag.id)
        # Line 3 - Elafgift
        account_tag = self.env.ref('l10n_dk.tag_tax_el')
        lines['elafgift'] = self.get_aml_account(options, account_tag.id)
        # Line 4 - Naturgas- og bygasafgift
        account_tag = self.env.ref('l10n_dk.tag_tax_natur_by_gas')
        lines['natur_by_gas_afgift'] = self.get_aml_account(options, account_tag.id)
        # Line 5 - Kulafgift
        account_tag = self.env.ref('l10n_dk.tag_tax_kul')
        lines['kulafgift'] = self.get_aml_account(options, account_tag.id)
        # Line 6 - CO2-afgift
        account_tag = self.env.ref('l10n_dk.tag_tax_co2')
        lines['co2_afgift'] = self.get_aml_account(options, account_tag.id)
        # Line 7 - Vandafgift
        account_tag = self.env.ref('l10n_dk.tag_tax_vand')
        lines['vandafgift'] = self.get_aml_account(options, account_tag.id)

    def get_supp_opl(self, options, lines):
        # Line 1 - Rubrik A = varer
        tax_tag = self.env.ref('l10n_dk.tag_tax_rubrik_av')
        lines['rubrik_av'] = self.get_aml_net(options, tax_tag.id)
        # Line 2 - Rubrik A = ydelser
        tax_tag = self.env.ref('l10n_dk.tag_tax_rubrik_ay')
        lines['rubrik_ay'] = self.get_aml_net(options, tax_tag.id)
        # Line 3 - Rubrik B = varer 
        tax_tag = self.env.ref('l10n_dk.tag_tax_rubrik_bv')
        lines['rubrik_bv'] = self.get_aml_net(options, tax_tag.id)
        # Line 4 - Rubrik B = varer
        tax_tag = self.env.ref('l10n_dk.tag_tax_rubrik_by')
        lines['rubrik_by'] = self.get_aml_net(options, tax_tag.id)
        # Line 5 - Rubrik B = ydelser
        tax_tag = self.env.ref('l10n_dk.tag_tax_rubrik_b_vy_u')
        lines['rubrik_b_vy_u'] = self.get_aml_net(options, tax_tag.id)
        # Line 6 - Rubrik C
        tax_tag = self.env.ref('l10n_dk.tag_tax_rubrik_c')
        lines['rubrik_c'] = self.get_aml_net(options, tax_tag.id)

    def get_aml_tax(self, options, tax_tag):
        self.env.cr.execute("""SELECT COALESCE(SUM(aml.debit-aml.credit), 0)
                                FROM account_move_line aml
                                INNER JOIN account_tax at ON (aml.tax_line_id = at.id)
                                INNER JOIN account_tax_account_tag atat ON (atat.account_tax_id = at.id)
                                INNER JOIN account_account_tag tag ON (atat.account_account_tag_id = tag.id)
                                WHERE aml.tax_exigible AND tag.id = %s AND aml.date >= '%s' AND aml.date <= '%s'
                                GROUP BY tag.id""" % (tax_tag, options['date_from'], options['date_to']))
        result = self.env.cr.fetchall()
        if len(result) < 1:
            return 0
        else:
            return abs(result[0][0])

    def get_aml_net(self, options, tax_tag):
        self.env.cr.execute("""SELECT COALESCE(SUM(aml.debit-aml.credit), 0)
                                FROM account_move_line aml
                                INNER JOIN account_move_line_account_tax_rel r ON (aml.id = r.account_move_line_id)
                                INNER JOIN account_tax at ON (r.account_tax_id = at.id)
                                INNER JOIN account_tax_account_tag atat ON (atat.account_tax_id = at.id)
                                INNER JOIN account_account_tag tag ON (atat.account_account_tag_id = tag.id)
                                WHERE aml.tax_exigible AND tag.id = %s AND aml.date >= '%s' AND aml.date <= '%s'
                                GROUP BY tag.id""" % (tax_tag, options['date_from'], options['date_to']))
        result = self.env.cr.fetchall()
        if len(result) < 1:
            return 0
        else:
            return abs(result[0][0])
            
    def get_aml_account(self, options, account_tag):
        self.env.cr.execute("""SELECT COALESCE(SUM(aml.debit-aml.credit), 0)
                                FROM account_move_line aml
                                INNER JOIN account_account aa ON (aml.account_id = aa.id)
                                INNER JOIN account_account_account_tag aaat ON (aa.id = aaat.account_account_id)
                                INNER JOIN account_account_tag tag ON (aaat.account_account_tag_id = tag.id)
                                WHERE tag.id = %s AND aml.date >= '%s' AND aml.date <= '%s'
                                GROUP BY tag.id""" % (account_tag, options['date_from'], options['date_to']))
        result = self.env.cr.fetchall()
        if len(result) < 1:
            return 0
        else:
            return abs(result[0][0])

class AccountTaxReport(models.TransientModel):
    _inherit = 'account.common.report'
    _name = 'account.tax.report.dk'
    _description = 'Danish Tax Report'

    def _print_report(self, data):
        
        return self.env.ref('l10n_dk_reports.print_l10n_dk_tax_report').report_action(self, data=data)