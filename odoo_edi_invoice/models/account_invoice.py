# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError
import logging

from odoo.tools import float_compare

_logger = logging.getLogger(__name__)

class odoo_edi_invoice(models.Model):
    _inherit = 'account.invoice'
    edi_document_id = fields.Char(compute='_compute_edi_document_id')

    is_edi = fields.Boolean(string="Is an EDI invoice", help="This indicates that the invoice is to be sent/recieved using EDI")
    gln = fields.Char(string='GLN number', help='GLN identification number of the partner. This can also be called the EAN identifier/number')
    odoo_edi_send_enable = fields.Boolean(
        string='Send EDI invoices to this customer',
        related="partner_id.odoo_edi_send_enable"
    )

    
    @api.multi
    def action_invoice_send_edi(self):
        for invoice in self:
            if not invoice.partner_id.odoo_edi_send_enable:
                if not invoice.partner_id.commercial_partner_id.odoo_edi_send_enable:
                    raise UserError(_("The partner, %s, is not configured for EDI invoicing") % invoice.partner_id.commercial_partner_id.name)
                #else:
                #    raise UserError(_("The partner, %s, is not configured for EDI invoicing") % invoice.partner_id.name)
            elif not invoice.partner_id.odoo_edi_method:
                if not invoice.partner_id.commercial_partner_id.odoo_edi_method:
                    raise UserError(_("The partner, %s, is not correctly configured for EDI invoicing.\nWe are missing the EDI Coummunication Method") % invoice.partner_id.commercial_partner_id.name)
                #else:
                #    raise UserError(_("The partner, %s, is not correctly configured for EDI invoicing.\nWe are missing the EDI Coummunication Method") % invoice.partner_id.name)
            if not invoice.payment_term_id:
                if not invoice.type == 'out_refund':
                    raise UserError(_('You must make sure to have payment terms set on your partner and the invoice'))
            if not invoice.date_due:
                raise UserError(_("We cannot send your EDI invoice, as your partner did not have payment terms configured upon invoice validation. Please either add the due date on the invoice or create a new invoice"))
            self.env['odoo_edi_invoice.document.invoice'].create_edi(invoice)
            invoice.sent = True
            invoice.message_post(body=_('Invoice <strong><em>{0}</em></strong> with Document ID <strong><em>{1}</em></strong> has been sent to GLN <strong><em>{2}</em></strong>'.format(invoice.number, invoice.edi_document_id, invoice._partner_gln()[0])), message_type='notification')

    def _compute_edi_document_id(self):
        for inv in self:
            company_registry = inv.company_id.company_registry
            inv.edi_document_id = company_registry + '-' + inv.number.replace('/', '')

    @api.one
    def _partner_gln(self):
        if self.partner_id.gln:
            return self.partner_id.gln
        elif self.partner_id.commercial_partner_id.gln:
            return self.partner_id.commercial_partner_id.gln
        else:
            return self.gln


    @api.multi
    def action_invoice_open(self):
        if self.partner_id.odoo_edi_send_enable or self.commercial_partner_id.odoo_edi_send_enable:
            return self.action_edi_invoice_open()
        else:
            return super(odoo_edi_invoice, self).action_invoice_open()


    @api.multi
    def action_edi_invoice_open(self):
        # More or less a validation action for sending EDI invoices, as this will simply check the invoices and return a list of errors if something is wrong
        # Otherwise it will run the normal account.invoice.action_invoice_open() method
        to_open_invoices = self.filtered(lambda inv: inv.state != 'open')
        if to_open_invoices.filtered(lambda inv: inv.state not in ['proforma2', 'draft']):
            raise UserError(
                _("Invoice must be in draft or Pro-forma state in order to validate it."))

        # Run EDI validation
        if not self.env.user.company_id.company_registry and not self.env.user.company_id.gln:
            raise UserError(
                _('The current company, %s, does not have a company registration number or GLN identification/number, which is required for EDI invoicing') % self.env.user.company_id.name)
        to_open_invoices.validate_edi_invoice()

        # Perform normal invoice opening/validation
        to_open_invoices.action_date_assign()
        to_open_invoices.action_move_create()
        return to_open_invoices.invoice_validate()

    @api.multi
    def validate_edi_invoice(self):
        for document in self:
            if not document.partner_id.odoo_edi_send_enable:
                if not document.partner_id.commercial_partner_id.odoo_edi_send_enable:
                    raise UserError(_("The partner, %s, is not configured for EDI invoicing") % document.partner_id.name)
            elif not document.partner_id.odoo_edi_method:
                if not document.partner_id.commercial_partner_id.odoo_edi_method:
                    raise UserError(_("The partner, %s, is not correctly configured for EDI invoicing.\nWe are missing the EDI Coummunication Method") % document.partner_id.name)
            if not document.partner_id.vat and not document.partner_id.gln:
            #if not document.partner_id.vat:
                if not document.partner_id.commercial_partner_id:
                    raise UserError(_('The partner, %s, does not have a company registration number or GLN identificaion/number, which is required for EDI invoicing') %
                                    document.partner_id.name)
                if not document.partner_id.commercial_partner_id.vat and not document.partner_id.commercial_partner_id.gln:
                    #if not document.partner_id.commercial_partner_id.vat:
                    raise UserError(_('The partner, %s, does not have a company registration number or GLN identificaion/number, which is required for EDI invoicing') %
                                    document.partner_id.commercial_partner_id.name)
            if not document.partner_id.phone:
                if not document.partner_id.commercial_partner_id:
                    raise UserError(_('The partner, %s, does not have a phone number registered on their account with us. This is required for EDI invoicing') % document.partner_id.name)
                if not document.partner_id.commercial_partner_id.phone:
                    raise UserError(_('The partner, %s, does not have a phone number registered on their account with us. This is required for EDI invoicing') % document.partner_id.commercial_partner_id.name)
            if not document.partner_id.email:
                if not document.partner_id.commercial_partner_id:
                    raise UserError(
                        _('The partner, %s, does not have an email address registered on their account with us. This is required for EDI invoicing') % document.partner_id.name)
                if not document.partner_id.commercial_partner_id.email:
                    raise UserError(
                        _('The partner, %s, does not have an email address registered on their account with us. This is required for EDI invoicing') % document.partner_id.commercial_partner_id.name)
            if hasattr(document, 'partner_shipping_id') and document.partner_shipping_id:
                if not document.partner_shipping_id.email:
                    if not document.partner_shipping_id.commercial_partner_id:
                        raise UserError(
                            _('The partner, %s, does not have an email address registered on their account with us. This is required for EDI invoicing') % document.partner_shipping_id.name)
                    if not document.partner_shipping_id.commercial_partner_id.email:
                        raise UserError(
                            _('The partner, %s, does not have an email address registered on their account with us. This is required for EDI invoicing') % document.partner_shipping_id.commercial_partner_id.name)

            if not document.name:
                raise UserError(
                    _('The invoice does not have a reference. Please set a reference before sending the invoice'))

            if not document.partner_id.property_payment_term_id:
                if not document.partner_id.commercial_partner_id.property_payment_term_id:
                    raise UserError(_('You must make sure to have payment terms set on your partner'))
            if not document.payment_term_id:
                raise UserError(_('You must make set the payment terms on this invoice before you can validate it'))

            line_errors = []
            for line in document.invoice_line_ids:
                if not line.uom_id.edi_name:
                    if not line.uom_id.name in line_errors:
                        line_errors.append(line.uom_id.name)

            if len(line_errors) > 0:
                raise UserError(_('The following units of measure, do not have a valid EDI unit name assigned. Please assign an EDI unit name to the listed units.\n %s') % ''.join(str(e)+'\n' for e in line_errors))
            document.is_edi = True
