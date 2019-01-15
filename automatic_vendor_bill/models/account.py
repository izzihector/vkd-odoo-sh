from odoo import models, fields, api
import logging
_logger = logging.getLogger(__name__)

class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    vendor_bill_mail_id = fields.Many2one('vendor.bill.mail')
    pdf_viewer = fields.Binary('PDF', compute="get_pdf_attachments")

    def get_pdf_attachments(self):
        # TODO handle multiple attached pdf files, currently only shows 1
        # Maybe merge separate pdf to a single file?
        for r in self:
            attachments = r.env['ir.attachment'].search([('res_model', '=', 'account.invoice'), ('res_id', '=', r.id)])
            for a in (x for x in attachments if '.pdf' in x.name or '.PDF' in x.name):
                r.pdf_viewer = a.datas

    @api.model
    def message_new(self, msg, custom_values=None):
        vendor_mail_id = self.env['vendor.bill.mail'].search([('id', '=', custom_values['vendor_bill_mail_id'])])

        # Separate the actual e-mail address from the 'from' field of msg
        msg_email = msg.get('from')
        if '<' in msg.get('from'):
            msg_email = msg_email.split('<')[1]
        if '>' in msg.get('from'):
            # msg_email = msg_email.split('>')[0]
            msg_email = msg_email.replace('>', '')

        partner = self.env['res.partner'].search([('email', 'ilike', msg_email)])

        if not partner or len(partner) > 1:
            partner = vendor_mail_id.default_contact

        account = vendor_mail_id.account_id
        journal = vendor_mail_id.journal_id
        company = vendor_mail_id.company_id
        responsible = vendor_mail_id.responsible

        # Pass the values to account.invoice record creation
        values = dict(custom_values or {}, user_id=responsible.id, company_id=company.id,
                                        partner_id=partner.id, account_id=account.id,
                                        journal_id=journal.id, type='in_invoice')
        res = super(AccountInvoice, self).message_new(msg, custom_values=values)
        return res

class VendorBillMail(models.Model):
    # A separate model for the incoming vendor bills is needed, because
    # creating the mail.alias.mixin on the account.invoice model will
    # create an alias for each record of the account.invoice model.
    # It also proved quite impossible to inherit mail.alias.mixin on
    # the res.company model.
    #
    # In order to make this feature multi-company compatible, and to ensure
    # the vendor bill is properly created, some fields are required to be set
    # on the vendor.bill.mail model. These fields are referenced when creating
    # the account.invoice record, when a mail is received.

    _name = 'vendor.bill.mail'
    _inherit = ['mail.thread', 'mail.alias.mixin']

    name = fields.Char(related="alias_name", readonly=True)
    company_id = fields.Many2one('res.company', string="Company", required=True)
    responsible = fields.Many2one('res.users', help="The user responsible for handling the incoming vendor bills. Do not set this to the administrator user", required=True)
    journal_id = fields.Many2one('account.journal', string="Journal", required=True)
    account_id = fields.Many2one('account.account', string="Account", required=True)
    alias_name = fields.Char(string="Alias Name", required=True)
    default_contact = fields.Many2one('res.partner', string="Default Contact", help="The default contact used, if the incoming email address can not be recognized.", required=True)

    def get_alias_model_name(self, vals):
        return ('account.invoice')

    def get_alias_values(self):

        values = super(VendorBillMail, self).get_alias_values()

        values['alias_defaults'] = {'vendor_bill_mail_id': self.id}
        values['alias_name'] = self.alias_name

        return values
