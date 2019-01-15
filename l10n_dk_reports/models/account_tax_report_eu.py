import logging
import re

_logger = logging.getLogger(__name__)
from odoo.exceptions import UserError

from odoo import models, fields, api, _


class EuReportTax(models.AbstractModel):
    _name = 'report.l10n_dk_reports.l10n_dk_tax_report_eu'

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
# 12 13
    @api.model
    def get_lines(self, options):
        lines = {}
        self.env.cr.execute("""SELECT rp.id, rp.vat, rc.id, tag.id, COALESCE(SUM(aml.debit-aml.credit), 0), rp.name
                                FROM account_move_line aml
                                INNER JOIN res_partner rp ON (aml.partner_id = rp.id)
                                INNER JOIN res_country rc ON (rp.country_id = rc.id)
                                INNER JOIN account_move_line_account_tax_rel r ON (aml.id = r.account_move_line_id)
                                INNER JOIN account_tax at ON (r.account_tax_id = at.id)
                                INNER JOIN account_tax_account_tag atat ON (atat.account_tax_id = at.id)
                                INNER JOIN account_account_tag tag ON (atat.account_account_tag_id = tag.id)
                                WHERE tag.id IN (%s, %s, %s) AND aml.date >= '%s' AND aml.date <= '%s'
                                GROUP BY rp.id, rp.name, rp.vat, rc.id, tag.id""" % (self.env.ref('l10n_dk.tag_tax_eu_sale').id,
                                                                                     self.env.ref('l10n_dk.tag_tax_eu_sale_service').id,
                                                                                     self.env.ref('l10n_dk.tag_tax_triangle').id,
                                                                                     options['date_from'], options['date_to']))
        results = self.env.cr.fetchall()
        _logger.info('RESULT: %s', results)
        for row in results:
            _logger.info('ROW: %s', row)
            if not row[1]:
                raise UserError(_("Missing VAT number for customer {0}.\n\nCommon reasons for error:\n1. Forgot to add VAT number on customer\n2. EU Sales tax on orders/invoices for non-EU or Danish customer.\n\nPlease make sure customer '{0}' has the correct VAT number, and that sales orders/invoices for the customer have the correct tax type".format(row[5])))
            index = row[0]
            if index not in lines:
                lines[index] = {'name': row[5], 'vat': re.sub('[^0-9]', '', row[1]), 'country': self.env['res.country'].browse(row[2]).name, 'eu_sale': 0, 'eu_sale_service': 0, 'triangle_trade': 0}
            if row[3] == self.env.ref('l10n_dk.tag_tax_eu_sale').id:
                lines[index]['eu_sale'] = int(abs(row[4]))
            if row[3] == self.env.ref('l10n_dk.tag_tax_eu_sale_service').id:
                lines[index]['eu_sale_service'] = int(abs(row[4]))
            if row[3] == self.env.ref('l10n_dk.tag_tax_triangle').id:
                lines[index]['triangle_trade'] = int(abs(row[4]))
        _logger.info('LINES: %s', lines)
        return lines
        

class AccountTaxReport(models.TransientModel):
    _inherit = 'account.common.report'
    _name = 'account.tax.report.dk.eu'
    _description = 'Danish EU Tax Report'

    def _print_report(self, data):
        return self.env.ref('l10n_dk_reports.print_l10n_dk_tax_report_eu').report_action(self, data=data)