# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from lxml import etree
import logging
from datetime import date
_logger = logging.getLogger(__name__)

class EdiInvoice(models.TransientModel):
    _name = 'odoo_edi_invoice.document.invoice'
    _inherit = 'odoo_edi.document'

    def create_edi(self, document):
        # if not document.partner_id.odoo_edi_send_enable:
        #     raise UserError(_("The partner, %s, is not configured for EDI invoicing") % document.partner_id.name)
        # elif not document.partner_id.odoo_edi_method:
        #     raise UserError(_("The partner, %s, is not correctly configured for EDI invoicing.\nWe are missing the EDI Coummunication Method") % document.partner_id.name)
        # self.validate_settings()
        # if not document.partner_id.vat and not document.partner_id.gln:
        #     if not document.partner_id.commercial_partner_id:
        #         raise UserError(_('The partner, %s, does not have a company registration number or GLN identificaion/number, which is required for EDI invoicing') %
        #                         document.partner_id.name)
        #     if not document.partner_id.commercial_partner_id.vat and not document.partner_id.commercial_partner_id.gln:
        #         raise UserError(_('The partner, %s, does not have a company registration number or GLN identification/number, which is required for EDI invoicing') %
        #                         document.partner_id.commercial_partner_id.name)
        if not document.partner_id.odoo_edi_send_enable:
            if not document.partner_id.commercial_partner_id.odoo_edi_send_enable:
                raise UserError(_("The partner, %s, is not configured for EDI invoicing") % document.partner_id.name)
        elif not document.partner_id.odoo_edi_method:
            if not document.partner_id.commercial_partner_id.odoo_edi_method:
                raise UserError(_("The partner, %s, is not correctly configured for EDI invoicing.\nWe are missing the EDI Coummunication Method") % document.partner_id.name)
        self.validate_settings()
        if not document.partner_id.vat and not document.partner_id.gln:
            if not document.partner_id.commercial_partner_id:
                raise UserError(
                    _('The partner, %s, does not have a company registration number or GLN identificaion/number, which is required for EDI invoicing') % document.partner_id.name)
            if not document.partner_id.commercial_partner_id.vat and not document.partner_id.commercial_partner_id.gln:
                raise UserError(_('The partner, %s, does not have a company registration number or GLN identificaion/number, which is required for EDI invoicing') %
                                document.partner_id.commercial_partner_id.name)
        if not document.partner_id.phone:
            if not document.partner_id.commercial_partner_id:
                raise UserError(
                    _('The partner, %s, does not have a phone number registered on their account with us. This is required for EDI invoicing') % document.partner_id.name)
            if not document.partner_id.commercial_partner_id.phone:
                raise UserError(_('The partner, %s, does not have a phone number registered on their account with us. This is required for EDI invoicing') %
                                document.partner_id.commercial_partner_id.name)
        if not document.partner_id.email:
            if not document.partner_id.commercial_partner_id:
                raise UserError(
                    _('The partner, %s, does not have an email address registered on their account with us. This is required for EDI invoicing') % document.partner_id.name)
            if not document.partner_id.commercial_partner_id.email:
                raise UserError(_('The partner, %s, does not have an email address registered on their account with us. This is required for EDI invoicing') %
                                document.partner_id.commercial_partner_id.name)
        if not document.payment_term_id:
            if not document.type == 'out_refund':
                raise UserError(_('You must make set the payment terms on this invoice before you can send it. This normally means that you have to cancel the invoice, validate it for edi and then send it again'))
        if hasattr(document, 'partner_shipping_id') and document.partner_shipping_id:
            if not document.partner_shipping_id.email:
                if not document.partner_shipping_id.commercial_partner_id:
                    raise UserError(
                        _('The partner, %s, does not have an email address registered on their account with us. This is required for EDI invoicing') % document.partner_shipping_id.name)
                if not document.partner_shipping_id.commercial_partner_id.email:
                    raise UserError(_('The partner, %s, does not have an email address registered on their account with us. This is required for EDI invoicing') %
                                    document.partner_shipping_id.commercial_partner_id.name)
        
        # ns0 = 'http://Edi-Portal/VKData/Documents/SalesInvoice'
        # rootNs = etree.QName(ns0, 'SalesInvoice_Custom_Xml')
        # doc = etree.Element(rootNs, nsmap={'ns0': 'http://Edi-Portal/VKData/Documents/SalesInvoice'
        #    })
        # invoice_endpoint_id = etree.SubElement(doc, 'EndpointId')
        # invoice_endpoint_id.text = document.partner_id.odoo_edi_method.name if document.partner_id.odoo_edi_method else document.partner_id.commercial_partner_id.odoo_edi_method.name
        # invoice_header = etree.SubElement(doc, 'Header')
        # self.create_invoice_header(document, invoice_header)
        # invoice_lines = etree.SubElement(doc, 'Lines')
        # self.create_invoice_lines(document.invoice_line_ids, invoice_lines, document)
        # processed_invoice = etree.tostring(doc, pretty_print=True, encoding=str)
        # self.send_document(processed_invoice, document.edi_document_id)
        doc = dict()
        # Document type for invoice is 2
        doc['DocType'] = 2
        doc['docID'] = document.number
        doc['docDate'] = document.date_invoice
        doc['msgFormat'] = document.partner_id.odoo_edi_method.document_type_id if document.partner_id.odoo_edi_method else document.partner_id.commercial_partner_id.odoo_edi_method.document_type_id
        # This is a predefined identification as agreed with our supplier
        doc['sourceModule'] = 'VK ODOO'
        # issuerParty is mostly 1, as we are the seller of the products/services being invoiced to the customer
        doc['issuerParty'] = 1
        doc['buyerParty'] = self.create_invoice_header_buyer(document)
        doc['sellerParty'] = self.create_invoice_header_supplier(document)
        doc['sellersOrderId'] = {
            'orderNo': document.origin
        }
        doc['ordReferences'] = {
            'buyersRef': document.name,
            'requisitionNo': ''
        }
        doc['deliveryParty'] = self.create_invoice_header_delivery(document)
        doc['invoiceParty'] = self.create_invoice_header_invoicee(document)
        doc['financialInfo'] = self.create_financial_info(document)
        doc['DetailLines'] = self.create_invoice_lines(document)
        # TODO: Create new method
        doc['documentTotals'] = self.create_invoice_totals(document)
        doc['paymentInfo'] = self.create_invoice_header_payment(document)

        self.send_document(doc, document.edi_document_id)

    # def create_invoice_header(self, invoice, invoice_header):
    #     originating_id = etree.SubElement(invoice_header, 'OriginatingId')
    #     originating_id.text = 'Odoo'
    #     invoice_number = etree.SubElement(invoice_header, 'InvoiceNumber')
    #     invoice_number.text = invoice.number
    #     invoice_date = etree.SubElement(invoice_header, 'InvoiceDate')
    #     invoice_date.text = date.strftime(invoice.date_invoice, "%Y-%m-%d")
    #     invoice_type = etree.SubElement(invoice_header, 'InvoiceType')
    #     if invoice.type == 'out_invoice':
    #         invoice_type.text = 'Invoice'
    #     else:
    #         if invoice.type == 'out_refund':
    #             invoice_type.text = 'CreditMemo'
    #     references = etree.SubElement(invoice_header, 'References')
    #     supplier_order_no = etree.SubElement(references, 'SupplierOrderNumber')
    #     if invoice.origin:
    #         supplier_order_no.text = invoice.origin
    #     else:
    #         supplier_order_no.text = invoice.number
    #     invoice_reference = etree.SubElement(references, 'BuyerOrderNumber')
    #     invoice_reference.text = invoice.name
    #     # self.create_embedded_invoice(invoice_header, invoice)
    #     # self.create_invoice_header_buyer(invoice_header, invoice)
    #     # self.create_invoice_header_delivery(invoice_header, invoice)
    #     # self.create_invoice_header_invoicee(invoice_header, invoice)
    #     # self.create_invoice_header_supplier(invoice_header, invoice)
    #     # self.create_invoice_header_payment(invoice_header, invoice)

    #     comment1 = etree.SubElement(invoice_header, "Comment1")
    #     if invoice.comment:
    #         comment1.text = invoice.comment
    #     comment2 = etree.SubElement(invoice_header, "Comment2")
    #     delivery_terms = etree.SubElement(invoice_header, "DeliveryTerms")
    #     delivery_terms.text = ""
    #     delivery_method = etree.SubElement(invoice_header, "DeliveryMethod")
    #     location = etree.SubElement(invoice_header, "Location")
    #     netweight = etree.SubElement(invoice_header, "NetWeightTotal")
    #     netweight.text = "0.00"
    #     grossweight = etree.SubElement(invoice_header, "GrossWeightTotal")
    #     grossweight.text = "0.00"
    #     currency = etree.SubElement(invoice_header, "CurrencyCode")
    #     currency.text = invoice.currency_id.name
    #     standard_vat = etree.SubElement(invoice_header, "StandardVatPercent")
    #     standard_vat.text = "25.0"
    #     self.create_invoice_header_amounts(invoice_header, invoice)


    def create_invoice_lines(self, invoice):
        lines = []
        for line in invoice.invoice_line_ids:
            l = dict()
            if not line.uom_id.edi_name:
                raise UserError(_("The Unit %s does not have an EDI unit assigned. Please assign an EDI unit definition before sending the invoice") % line.uom_id.name)
            currency = line.invoice_id and line.invoice_id.currency_id or None
            price = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
            taxes = line.invoice_line_tax_ids.compute_all(price, currency, line.quantity, product=line.product_id, partner=line.invoice_id.partner_id)
            # l = etree.SubElement(invoice_lines, 'Line')
            # line_id = etree.SubElement(l, 'LineId')
            # line_id.text = str(line.id)
            # line_qty = etree.SubElement(l, 'Qty')
            # line_qty.text = str(line.quantity)
            l['qtyTu'] = line.quantity
            # line_uom = etree.SubElement(l, 'UnitOfMeasure')
            # line_uom.text = line.uom_id.edi_name.name
            l['unit'] = line.uom_id.edi_name.name
            # line_brand = etree.SubElement(l, 'BrandName')
            # line_item = etree.SubElement(l, 'ItemName')
            # line_item.text = line.product_id.name
            l['sellersItemNo'] = line.product_id.default_code
            # line_desc = etree.SubElement(l, 'ItemDescription')
            # line_desc.text = line.name
            l['description'] = line.name
            # line_comment = etree.SubElement(l, 'Comment')
            # line_comment.text = ''
            # line_references = etree.SubElement(l, 'References')
            # line_references_ref = etree.SubElement(line_references, 'BuyerOrderNumber')
            l['delDate'] = invoice.date_invoice
            # line_references_ref.text = invoice.name
            # line_amounts = etree.SubElement(l, 'Amounts')
            # NetUnitPrice is the unit price with any applicable discounts applied
            # line_amounts_net_price = etree.SubElement(line_amounts, 'NetUnitPrice')
            # line_amounts_net_price.text = str(line.price_unit - (line.price_unit * ((line.discount or 0.0) / 100.0)))
            l['netPrice'] = line.price_unit - (line.price_unit * ((line.discount or 0.0) / 100.0))
            # GrossUnitPrice is the unit price of the product with no modifications done
            # line_amounts_gross_price = etree.SubElement(line_amounts, 'GrossUnitPrice')
            # line_amounts_gross_price.text = str(line.price_unit)
            l['grossPrice'] = line.price_unit

            # line_vat_pct = etree.SubElement(line_amounts, 'VatPercent')
            # line_vat_pct.text = str(round(taxes['taxes'][0]['amount'] / line.price_subtotal * 100, 2)) if 0 in taxes['taxes'] else str(0)
            # line_vat_amount = etree.SubElement(line_amounts, 'VatAmount')
            # line_vat_amount.text = str(taxes['taxes'][0]['amount']) if 0 in taxes['taxes'] else str(0)
            l['vatAmount'] = taxes['taxes'][0]['amount'] if 0 in taxes['taxes'] else 0
            # line_amounts_taxable = etree.SubElement(line_amounts, 'TaxAbleAmount')
            # line_amounts_taxable.text = str(line.price_subtotal)
            # line_amounts_subtotal = etree.SubElement(line_amounts, 'LineAmount')
            # line_amounts_subtotal.text = str(line.price_subtotal)
            l['netAmount'] = line.price_subtotal
            # line_amounts_disc_amount = etree.SubElement(line_amounts, 'DiscountAmount')
            # line_amounts_disc_amount.text = str(line.price_unit * ((line.discount or 0.0) / 100.0) * line.quantity)
            # line_amounts_disc_pct = etree.SubElement(line_amounts, 'DiscountPercent')
            # line_amounts_disc_pct.text = str(line.discount)
            l['discPct'] = line.discount

            lines.append(l)
        return lines

    def create_invoice_header_buyer(self, invoice):
        buyer = dict()
        # buyer_endpoint_type = etree.SubElement(buyer, 'EndpointType')
        buyer['accountNo'] = invoice.partner_id.ref if invoice.partner_id.ref else invoice.partner_id.commercial_partner_id.ref
        if not buyer['accountNo']:
            buyer['accountNo'] = str(invoice.partner_id.id)
        # buyer_gln_no = etree.SubElement(buyer, 'Gln')
        buyer['GLN'] = invoice.partner_id.gln if invoice.partner_id.gln else invoice.partner_id.commercial_partner_id.gln
        # if invoice.partner_id.gln:
        #     buyer_gln_no.text = invoice.partner_id.gln
        # elif invoice.partner_id.commercial_partner_id.gln:
        #     buyer_gln_no.text = invoice.partner_id.commercial_partner_id.gln
        # buyer_vat_no = etree.SubElement(buyer, 'Cvr')
        buyer['natTaxNo'] = invoice.partner_id.vat if invoice.partner_id.vat else invoice.partner_id.commercial_partner_id.vat
        # if invoice.partner_id.vat:
        #     buyer_vat_no.text = invoice.partner_id.vat
        # else:
        #     if invoice.partner_id.commercial_partner_id.vat:
        #         buyer_vat_no.text = invoice.partner_id.commercial_partner_id.vat
        #     else:
        #         buyer_vat_no.text = ''
        # buyer_account_no = etree.SubElement(buyer, 'AccountNumber')
        # if invoice.partner_id.ref:
        #     buyer_account_no.text = invoice.partner_id.ref
        # else:
        #     if invoice.partner_id.commercial_partner_id.ref:
        #         buyer_account_no.text = invoice.partner_id.commercial_partner_id.ref
        #     else:
        #         buyer_account_no.text = str(invoice.partner_id.id)
        # buyer_name = etree.SubElement(buyer, 'Name')
        # buyer_name.text = invoice.partner_id.name if invoice.partner_id.name else invoice.partner_id.commercial_partner_id.name
        buyer['name'] = invoice.partner_id.name if invoice.partner_id.name else invoice.partner_id.commercial_partner_id.name
        # buyer_address = etree.SubElement(buyer, 'Address')
        # buyer_address.text = invoice.partner_id.street if invoice.partner_id.street else invoice.partner_id.commercial_partner_id.street
        buyer['address1'] = invoice.partner_id.street if invoice.partner_id.street else invoice.partner_id.commercial_partner_id.street
        if invoice.partner_id.street2 or invoice.partner_id.commercial_partner_id.street2:
            buyer['address2'] = invoice.partner_id.street2 if invoice.partner_id.street2 else invoice.partner_id.commercial_partner_id.street2
        # buyer_state = etree.SubElement(buyer, 'State')
        # if invoice.partner_id.state_id.name:
        #     buyer_state.text = invoice.partner_id.state_id.name
        # buyer_zipcode = etree.SubElement(buyer, 'ZipCode')
        # buyer_zipcode.text = invoice.partner_id.zip if invoice.partner_id.zip else invoice.partner_id.commercial_partner_id.zip
        buyer['zipCode'] = invoice.partner_id.zip if invoice.partner_id.zip else invoice.partner_id.commercial_partner_id.zip
        # buyer_city = etree.SubElement(buyer, 'City')
        # buyer_city.text = invoice.partner_id.city if invoice.partner_id.city else invoice.partner_id.commercial_partner_id.city
        buyer['city'] = invoice.partner_id.city if invoice.partner_id.city else invoice.partner_id.commercial_partner_id.city
        # buyer_country = etree.SubElement(buyer, 'Country')
        if invoice.partner_id.country_id:
            # buyer_country.text = invoice.partner_id.country_id.code
            buyer['country'] = invoice.partner_id.country_id.code
        elif invoice.partner_id.commercial_partner_id.country_id:
            # buyer_country.text = invoice.partner_id.commercial_partner_id.country_id.code
            buyer['country'] = invoice.partner_id.commercial_partner_id.country_id.code
        else:
            raise UserError(_('You have to set a country on the customer'))
        # buyer_contact = etree.SubElement(buyer, 'Contact')
        # buyer_contact_id = etree.SubElement(buyer_contact, 'ContactID')
        # buyer_contact_id.text = str(invoice.partner_id.id)
        # buyer_contact_name = etree.SubElement(buyer_contact, 'ContactName')
        # buyer_contact_name.text = invoice.partner_id.name if invoice.partner_id.name else invoice.partner_id.commercial_partner_id.name
        buyer['contact'] = invoice.partner_id.name if invoice.partner_id.company_type == 'person' else ''
        if invoice.partner_id.phone:
            # buyer_contact_phone = etree.SubElement(
            #     buyer_contact, 'ContactTelephone')
            # buyer_contact_phone.text = invoice.partner_id.phone if invoice.partner_id.phone else invoice.partner_id.commercial_partner_id.phone
            buyer['phone'] = invoice.partner_id.phone if invoice.partner_id.phone else invoice.partner_id.commercial_partner_id.phone
        if invoice.partner_id.email:
            # buyer_contact_email = etree.SubElement(buyer_contact, 'ContactEmail')
            # buyer_contact_email.text = invoice.partner_id.email if invoice.partner_id.email else invoice.partner_id.commercial_partner_id.email
            buyer['eMail'] = invoice.partner_id.email if invoice.partner_id.email else invoice.partner_id.commercial_partner_id.email
        return buyer

    def create_invoice_header_invoicee(self, invoice):
        # invoicee = etree.SubElement(invoice_header, 'Invoicee')
        invoicee = dict()
        # invoice_endpoint_type = etree.SubElement(invoicee, 'EndpointType')
        # invoicee_gln_no = etree.SubElement(invoicee, 'Gln')
        invoicee['GLN'] = invoice._partner_gln()[0]
        # if invoice.gln:
        #     invoicee_gln_no.text = invoice.gln
        # elif invoice.partner_id.gln:
        #     invoicee_gln_no.text = invoice.partner_id.gln
        # elif invoice.partner_id.commercial_partner_id.gln:
        #     invoicee_gln_no.text = invoice.partner_id.commercial_partner_id.gln
        # invoicee_vat_no = etree.SubElement(invoicee, 'Cvr')
        if invoice.partner_id.vat:
            invoicee['natTaxNo'] = invoice.partner_id.vat
        else:
            if invoice.partner_id.commercial_partner_id.vat:
                invoicee['natTaxNo'] = invoice.partner_id.commercial_partner_id.vat
            else:
                invoicee['natTaxNo'] = ''
        # invoicee_account_no = etree.SubElement(invoicee, 'AccountNumber')
        if invoice.partner_id.ref:
            invoicee['accountNo'] = invoice.partner_id.ref
        else:
            if invoice.partner_id.commercial_partner_id.ref:
                invoicee['accountNo'] = invoice.partner_id.commercial_partner_id.ref
            else:
                invoicee['accountNo'] = str(invoice.partner_id.id)
        # invoicee_name = etree.SubElement(invoicee, 'Name')
        invoicee['name'] = invoice.partner_id.name if invoice.partner_id.name else invoice.partner_id.commercial_partner_id.name
        # invoicee_address = etree.SubElement(invoicee, 'Address')
        invoicee['address1'] = invoice.partner_id.street if invoice.partner_id.street else invoice.partner_id.commercial_partner_id.street
        if invoice.partner_id.street2 or invoice.partner_id.commercial_partner_id.street2:
            invoicee['address2'] = invoice.partner_id.street2 if invoice.partner_id.street2 else invoice.partner_id.commercial_partner_id.street2
        # invoicee_state = etree.SubElement(invoicee, 'State')
        # if invoice.partner_id.state_id.name:
        #     invoicee_state.text = invoice.partner_id.state_id.name
        # invoicee_zipcode = etree.SubElement(invoicee, 'ZipCode')
        invoicee['zipCode'] = invoice.partner_id.zip if invoice.partner_id.zip else invoice.partner_id.commercial_partner_id.zip
        # invoicee_city = etree.SubElement(invoicee, 'City')
        invoicee['city'] = invoice.partner_id.city if invoice.partner_id.city else invoice.partner_id.commercial_partner_id.city
        # invoicee_country = etree.SubElement(invoicee, 'Country')
        if invoice.partner_id.country_id:
            invoicee['country'] = invoice.partner_id.country_id.code
        elif invoice.partner_id.commercial_partner_id.country_id:
            invoicee['country'] = invoice.partner_id.commercial_partner_id.country_id.code
        else:
            raise UserError(_('You have to set a country on the customer'))
        # invoicee_contact = etree.SubElement(invoicee, 'Contact')
        # invoicee_contact_id = etree.SubElement(
        #     invoicee_contact, 'ContactID')
        # invoicee_contact_id.text = str(invoice.partner_id.id)
        # invoicee_contact_name = etree.SubElement(invoicee_contact, 'ContactName')
        # invoicee_contact_name.text = invoice.partner_id.name if invoice.partner_id.name else invoice.partner_id.commercial_partner_id.name
        invoicee['contact'] = invoice.partner_id.name if invoice.partner_id.company_type == 'person' else ''
        if invoice.partner_id.phone:
            # invoicee_contact_phone = etree.SubElement(
            #     invoicee_contact, 'ContactTelephone')
            invoicee['phone'] = invoice.partner_id.phone if invoice.partner_id.phone else invoice.partner_id.commercial_partner_id.phone
        if invoice.partner_id.email:
            # invoicee_contact_email = etree.SubElement(
            #     invoicee_contact, 'ContactEmail')
            invoicee['eMail'] = invoice.partner_id.email if invoice.partner_id.email else invoice.partner_id.commercial_partner_id.email
        return invoicee

    def create_invoice_header_delivery(self, invoice):
        delivery = dict()
        if hasattr(invoice, 'partner_shipping_id') and invoice.partner_shipping_id.id:
            # delivery = etree.SubElement(invoice_header, 'Delivery')
            # delivery_endpoint_type = etree.SubElement(delivery, 'EndpointType')
            # delivery_gln_no = etree.SubElement(delivery, 'Gln')
            if invoice.partner_shipping_id.gln:
                delivery['GLN'] = invoice.partner_shipping_id.gln
            elif invoice.partner_shipping_id.commercial_partner_id.gln:
                delivery['GLN'] = invoice.partner_shipping_id.commercial_partner_id.gln
            # delivery_vat_no = etree.SubElement(delivery, 'Cvr')
            if invoice.partner_shipping_id.vat:
                delivery['natTaxNo'] = invoice.partner_shipping_id.vat
            elif invoice.partner_shipping_id.commercial_partner_id.vat:
                delivery['natTaxNo'] = invoice.partner_shipping_id.commercial_partner_id.vat
            # delivery_account_no = etree.SubElement(delivery, 'AccountNumber')
            if invoice.partner_shipping_id.ref:
                # delivery_account_no.text = invoice.partner_shipping_id.ref
                delivery['accountNo'] = invoice.partner_shipping_id.ref
            else:
                if invoice.partner_shipping_id.commercial_partner_id.ref:
                    # delivery_account_no.text = invoice.partner_shipping_id.commercial_partner_id.ref
                    delivery['accountNo'] = invoice.partner_shipping_id.commercial_partner_id.ref
            # delivery_name = etree.SubElement(delivery, 'Name')
            # delivery_name.text = invoice.partner_shipping_id.name if invoice.partner_shipping_id.name else invoice.partner_shipping_id.commercial_partner_id.name
            delivery['name'] = invoice.partner_shipping_id.name if invoice.partner_shipping_id.name else invoice.partner_shipping_id.commercial_partner_id.name
            # delivery_address = etree.SubElement(delivery, 'Address')
            # delivery_address.text = invoice.partner_shipping_id.street if invoice.partner_shipping_id.street else invoice.partner_shipping_id.commercial_partner_id.street
            delivery['address1'] = invoice.partner_shipping_id.street if invoice.partner_shipping_id.street else invoice.partner_shipping_id.commercial_partner_id.street
            if invoice.partner_id.street2 or invoice.partner_id.commercial_partner_id.street2:
                delivery['address2'] = invoice.partner_shipping_id.street2 if invoice.partner_shipping_id.street2 else invoice.partner_shipping_id.commercial_partner_id.street2
            # delivery_state = etree.SubElement(delivery, 'State')
            # if invoice.partner_shipping_id.state_id.name:
            #     delivery_state.text = invoice.partner_shipping_id.state.name
            # delivery_zipcode = etree.SubElement(delivery, 'ZipCode')
            # delivery_zipcode.text = invoice.partner_shipping_id.zip if invoice.partner_shipping_id.zip else invoice.partner_shipping_id.commercial_partner_id.zip
            delivery['zipCode'] = invoice.partner_shipping_id.zip if invoice.partner_shipping_id.zip else invoice.partner_shipping_id.commercial_partner_id.zip
            # delivery_city = etree.SubElement(delivery, 'City')
            # delivery_city.text = invoice.partner_shipping_id.city if invoice.partner_shipping_id.city else invoice.partner_shipping_id.commercial_partner_id.city
            delivery['city'] = invoice.partner_shipping_id.city if invoice.partner_shipping_id.city else invoice.partner_shipping_id.commercial_partner_id.city
            # delivery_country = etree.SubElement(delivery, 'Country')
            if invoice.partner_shipping_id.country_id:
                # delivery_country.text = invoice.partner_shipping_id.country_id.code
                delivery['country'] = invoice.partner_shipping_id.country_id.code
            elif invoice.partner_shipping_id.commercial_partner_id.country_id:
                # delivery_country.text = invoice.partner_shipping_id.commercial_partner_id.country_id.code
                delivery['country'] = invoice.partner_shipping_id.commercial_partner_id.country_id.code
            else:
                raise UserError(_('You have to set a country on the shipping address'))
            # delivery_contact = etree.SubElement(delivery, 'Contact')
            # delivery_contact_id = etree.SubElement(delivery_contact, 'ContactID')
            # delivery_contact_id.text = str(invoice.partner_shipping_id.id)
            # delivery_contact_name = etree.SubElement(
            #     delivery_contact, 'ContactName')
            # delivery_contact_name.text = invoice.partner_shipping_id.name if invoice.partner_shipping_id.name else invoice.partner_shipping_id.commercial_partner_id.name
            delivery['contact'] = invoice.partner_shipping_id.name if invoice.partner_shipping_id.company_type == 'person' else ''
        else:
            # delivery = etree.SubElement(invoice_header, 'Delivery')
            # delivery_endpoint_type = etree.SubElement(delivery, 'EndpointType')
            # delivery_gln_no = etree.SubElement(delivery, 'Gln')
            # if invoice.partner_id.gln:
            #     delivery_gln_no.text = invoice.partner_id.gln
            # elif invoice.partner_id.commercial_partner_id.gln:
            #     delivery_gln_no.text = invoice.partner_id.commercial_partner_id.gln
            if invoice.partner_id.gln:
                delivery['GLN'] = invoice.partner_id.gln
            elif invoice.partner_id.commercial_partner_id.gln:
                delivery['GLN'] = invoice.partner_id.commercial_partner_id.gln
            # delivery_vat_no = etree.SubElement(delivery, 'Cvr')
            if invoice.partner_id.vat:
                delivery['natTaxNo'] = invoice.partner_id.vat
            elif invoice.partner_id.commercial_partner_id.vat:
                delivery['natTaxNo'] = invoice.partner_id.commercial_partner_id.vat
            #     delivery_vat_no.text = invoice.partner_id.vat
            # elif invoice.partner_id.commercial_partner_id.vat:
            #     delivery_vat_no.text = invoice.partner_id.commercial_partner_id.vat
            # delivery_account_no = etree.SubElement(delivery, 'AccountNumber')
            if invoice.partner_id.ref:
                delivery['accountNo'] = invoice.partner_id.ref
            else:
                if invoice.partner_id.commercial_partner_id.ref:
                    delivery['accountNo'] = invoice.partner_id.commercial_partner_id.ref
                else:
                    delivery['accountNo'] = str(invoice.partner_id.id)
            # delivery_name = etree.SubElement(delivery, 'Name')
            # delivery_name.text = invoice.partner_id.name if invoice.partner_id.name else invoice.partner_id.commercial_partner_id.name
            delivery['name'] = invoice.partner_id.name if invoice.partner_id.name else invoice.partner_id.commercial_partner_id.name
            # delivery_address = etree.SubElement(delivery, 'Address')
            # delivery_address.text = invoice.partner_id.street if invoice.partner_id.street else invoice.partner_id.commercial_partner_id.street
            delivery['address1'] = invoice.partner_id.street if invoice.partner_id.street else invoice.partner_id.commercial_partner_id.street
            if invoice.partner_id.street2 or invoice.partner_id.commercial_partner_id.street2:
                delivery['address2'] = invoice.partner_id.street2 if invoice.partner_id.street2 else invoice.partner_id.commercial_partner_id.street2
            # delivery_state = etree.SubElement(delivery, 'State')
            # if invoice.partner_id.state_id.name:
            #     delivery_state.text = invoice.partner_id.state.name
            # delivery_zipcode = etree.SubElement(delivery, 'ZipCode')
            # delivery_zipcode.text = invoice.partner_id.zip if invoice.partner_id.zip else invoice.partner_id.commercial_partner_id.zip
            delivery['zipCode'] = invoice.partner_id.zip if invoice.partner_id.zip else invoice.partner_id.commercial_partner_id.zip
            # delivery_city = etree.SubElement(delivery, 'City')
            # delivery_city.text = invoice.partner_id.city if invoice.partner_id.city else invoice.partner_id.commercial_partner_id.city
            delivery['city'] = invoice.partner_id.city if invoice.partner_id.city else invoice.partner_id.commercial_partner_id.city
            # delivery_country = etree.SubElement(delivery, 'Country')
            if invoice.partner_id.country_id:
                # delivery_country.text = invoice.partner_id.country_id.code
                delivery['country'] = invoice.partner_id.country_id.code
            elif invoice.partner_id.commercial_partner_id.country_id:
                # delivery_country.text = invoice.partner_id.commercial_partner_id.country_id.code
                delivery['country'] = invoice.partner_id.commercial_partner_id.country_id.code
            else:
                raise UserError(_('You have to set a country on the customer'))
            # delivery_contact = etree.SubElement(delivery, 'Contact')
            # delivery_contact_id = etree.SubElement(delivery_contact, 'ContactID')
            # delivery_contact_id.text = str(invoice.partner_id.id)
            # delivery_contact_name = etree.SubElement(
            #     delivery_contact, 'ContactName')
            # delivery_contact_name.text = invoice.partner_id.name if invoice.partner_id.name else invoice.partner_id.commercial_partner_id.name
            delivery['contact'] = invoice.partner_id.name if invoice.partner_id.company_type == 'person' else ''
        return delivery

    def create_invoice_header_supplier(self, invoice):
        # company = etree.SubElement(invoice_header, 'Supplier')
        company = dict()
        # company_endpoint_type = etree.SubElement(company, 'EndpointType')
        # company_gln_no = etree.SubElement(company, 'Gln')
        if invoice.company_id.gln:
            company['GLN'] = invoice.company_id.gln
        else:
            company['GLN'] = ""
        # company_vat_no = etree.SubElement(company, 'Cvr')
        if invoice.company_id.company_registry:
            company['natTaxNo'] = invoice.company_id.company_registry if invoice.company_id.company_registry[:2] == invoice.company_id.country_id.code else invoice.company_id.country_id.code + invoice.company_id.company_registry
        # company_account_no = etree.SubElement(company, 'AccountNumber')
        # company_name = etree.SubElement(company, 'Name')
        # company_name.text = invoice.company_id.name
        company['name'] = invoice.company_id.name
        # company_address = etree.SubElement(company, 'Address')
        # company_address.text = invoice.company_id.street
        company['address1'] = invoice.company_id.street
        if invoice.company_id.street2:
            company['address2'] = invoice.company_id.street2
        # company_state = etree.SubElement(company, 'State')
        # if invoice.company_id.state_id.name:
        #     company_state.text = invoice.company_id.state_id.name
        # company_zipcode = etree.SubElement(company, 'ZipCode')
        # company_zipcode.text = invoice.company_id.zip
        company['zipCode'] = invoice.company_id.zip
        # company_city = etree.SubElement(company, 'City')
        # company_city.text = invoice.company_id.city
        company['city'] = invoice.company_id.city
        # company_country = etree.SubElement(company, 'Country')
        # company_country.text = invoice.company_id.country_id.code
        company['country'] = invoice.company_id.country_id.code
        # company_contact = etree.SubElement(company, 'Contact')
        #company_contact_name = etree.SubElement(company_contact, 'ContactName')
        company['contact'] = ''
        if invoice.company_id.phone:
            # company_contact_phone = etree.SubElement(
            #     company_contact, 'ContactTelephone')
            # company_contact_phone.text = invoice.company_id.phone
            company['phone'] = invoice.company_id.phone
        if invoice.company_id.email:
            # company_contact_email = etree.SubElement(
            #     company_contact, 'ContactEmail')
            # company_contact_email.text = invoice.company_id.email
            company['eMail'] = invoice.company_id.email
        return company

    def create_invoice_header_payment(self, invoice):
        payment = dict()
        # iban_no = ""
        # payment = etree.SubElement(invoice_header, "Payment")

        # payment_due_date = etree.SubElement(payment, "PaymentDueDate")
        # payment_due_date.text = date.strftime(invoice.date_due, "%Y-%m-%d")
        # if invoice.payment_term_id:
        #     payment_note = etree.SubElement(payment, "Note")
        #     payment_note.text = invoice.payment_term_id.note if invoice.payment_term_id.note else invoice.payment_term_id.name
        #FIK payment information
        #payment_fik = etree.SubElement(payment, "FIK")
        #payment_fik_instruction_id = etree.SubElement(payment_fik, "InstructionId")
        #payment_fik_id = etree.SubElement(payment_fik, "PaymentId")
        #payment_fik_account = etree.SubElement(payment_fik, "AccountId")

        # payment_bank = etree.SubElement(payment, "BankAccount")
        # payment_bank_reg = etree.SubElement(payment_bank, "Reg")
        # payment_bank_no = etree.SubElement(payment_bank, "No")
        # payment_iban = etree.SubElement(payment, "IBAN")
        # payment_iban_no = etree.SubElement(payment_iban, "No")
        if invoice.partner_id.bank_journal_id.bank_acc_number:
            bank_acc = invoice.partner_id.bank_journal_id.bank_account_id
            # payment_bank_reg.text = bank_acc.get_bban()[:4]
            payment['paymBankReg'] = bank_acc.get_bban()[:4]
            # payment_bank_no.text = bank_acc.get_bban().replace(payment_bank_reg.text, '')
            payment['paymBankAcc'] = bank_acc.get_bban().replace(payment['paymBankReg'], '')
            payment['paymIBAN'] = invoice.partner_id.bank_journal_id.bank_acc_number
        elif invoice.company_id.bank_journal_id.bank_acc_number:
            bank_acc = invoice.company_id.bank_journal_id.bank_account_id
            # payment_bank_reg.text = bank_acc.get_bban()[:4]
            payment['paymBankReg'] = bank_acc.get_bban()[:4]
            # payment_bank_no.text = bank_acc.get_bban().replace(payment_bank_reg.text, '')
            payment['paymBankAcc'] = bank_acc.get_bban().replace(payment['paymBankReg'], '')
            payment['paymIBAN'] = invoice.company_id.bank_journal_id.bank_acc_number
        # payment_iban_bic = etree.SubElement(payment_iban, "BIC")
        if invoice.partner_id.bank_journal_id.bank_id.bic:
            payment['paymSwift'] = invoice.partner_id.bank_journal_id.bank_id.bic
        elif invoice.company_id.bank_journal_id.bank_id.bic:
            payment['paymSwift'] = invoice.company_id.bank_journal_id.bank_id.bic
        return payment

    # def create_invoice_header_amounts(self, invoice_header, invoice):
    #     amounts = etree.SubElement(invoice_header, "Amounts")
    #     charges = etree.SubElement(amounts, "Charges")
    #     allowance = etree.SubElement(amounts, "Allowances")
    #     tax_groups = etree.SubElement(amounts, "TaxGroups")
    #     self.create_invoice_header_amounts_taxgroups(tax_groups, invoice)
    #     amounts_total = etree.SubElement(amounts, "Totals")
    #     amounts_total_amount = etree.SubElement(amounts_total, "TotalAmount")
    #     amounts_total_amount.text = str(invoice.amount_total)
    #     amounts_total_tax = etree.SubElement(amounts_total, "TotalTaxAmount")
    #     amounts_total_tax.text = str(invoice.amount_tax)
    #     amounts_total_taxable = etree.SubElement(amounts_total, "TotalTaxableAmount")
    #     amounts_total_taxable.text = str(invoice.amount_untaxed)
    #     amounts_line_total = etree.SubElement(amounts_total, "TotalLineAmount")
    #     amounts_line_total.text = str(invoice.amount_untaxed)
    #     amounts_total_excl_vat = etree.SubElement(
    #         amounts_total, "TotalAmountExclVat")
    #     amounts_total_excl_vat.text = str(invoice.amount_untaxed)

    # def create_invoice_header_amounts_taxgroups(self, tax_groups, invoice):
    #     tax_types = dict()
    #     for t in invoice.tax_line_ids:
    #         if  str(t.tax_id.amount) in tax_types:
    #             tax_types[str(t.tax_id.amount)]["base"] += t.base
    #             tax_types[str(t.tax_id.amount)]["amount"] += t.amount
    #         else:
    #             tax_types[str(t.tax_id.amount)] = {
    #                 'percentage': t.tax_id.amount,
    #                 'base': t.base,
    #                 'amount': t.amount
    #             }
    #     for tx in tax_types:
    #         print(tx)
    #         tax = etree.SubElement(tax_groups, "Tax")
    #         tax_percent = etree.SubElement(tax, "Percent")
    #         tax_percent.text = str(tax_types[tx]["percentage"])
    #         tax_taxable_amount = etree.SubElement(tax, "TaxableAmount")
    #         tax_taxable_amount.text = str(tax_types[tx]["base"])
    #         tax_tax_amount = etree.SubElement(tax, "TaxAmount")
    #         tax_tax_amount.text = str(tax_types[tx]["amount"])

    def create_embedded_invoice(self, invoice_header, invoice):
        pass

    def create_financial_info(self, invoice):
        financial = dict()
        financial['currency'] = invoice.currency_id.name
        financial['vatDutiable'] = True if invoice.tax_line_ids else False
        financial['vatPercent'] = 25.0 if invoice.tax_line_ids else 0.0
        return financial

    def create_invoice_totals(self, invoice):
        totals = dict()
        totals['orderBalance'] = invoice.amount_untaxed
        totals['vatBaseAmount'] = invoice.amount_untaxed
        totals['vatAmount'] = invoice.amount_tax
        totals['invoiceAmount'] = invoice.amount_total
        totals['dueDate'] = invoice.date_due
        return totals
