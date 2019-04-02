# -*- coding: utf-8 -*-
from odoo import models, fields, api
# Import the API root from another module
from odoo.addons.odoo_edi.models.edi_document import API_ROOT
import logging, json, requests, datetime
_logger = logging.getLogger(__name__)

class EdiVendorBills(models.Model):
    _name = 'odoo_edi_vendor_bill.document.vendorbill'
    _inherit = 'odoo_edi.document'

    def recieve_document(self):
        token = self.env.user.company_id.odoo_edi_token
        headers = {
            'Content-Type': 'application/json; charset=utf8',
            'Authorization': 'Bearer {0}'.format(token)
        }
        server_address = API_ROOT + "/document/getpendingdoclist"
        result = requests.get(server_address, headers=headers)
        if not result.status_code == 200:
            _logger.info('Error during request:')
            _logger.info(result)
        _logger.info(result.status_code)
        json = result.json()

        for val in json:
            server_address = API_ROOT + "/document/{id}".format(id=val['conversationID'])
            result = requests.get(server_address, headers=headers)
            document = result.json()
            # We do only want to process invoices
            if document['DocType'] == 2:
                # This piece of code is used to obtain the vendor id
                # p_id = self.env['res.partner'].search([('name', '=', sellerparty_name)])
                # First try to find the vendor/supplier based on their VAT number
                partner_id = self.env['res.partner'].search([('vat', '=', document['Invoice']['sellerParty']['natTaxNo']), ('supplier', '=', True)])
                # If nothing is found, we prepend the country code to take in to account
                # the case where the international version of the VAT number has been used in Odoo
                if not partner_id.id:
                    _logger.warn('Could not find partner based in raw VAT: {}'.format(
                        document['Invoice']['sellerParty']['natTaxNo']))
                    partner_id = self.env['res.partner'].search([('vat', '=', str(document['Invoice']['sellerParty']['country']).upper() + document['Invoice']['sellerParty']['natTaxNo']), ('supplier', '=', True)])
                    # Finally if this will also not find it for us, then we try to find them based on the GLN
                    if not partner_id.id:
                        _logger.warn('Could not find partner based in raw VAT with country code: {}'.format(
                            str(document['Invoice']['sellerParty']['country']).upper() + document['Invoice']['sellerParty']['natTaxNo']))
                        partner_id = self.env['res.partner'].search([('gln', '=', document['Invoice']['sellerParty']['GLN']), ('supplier', '=', True)])
                # Finally we have to make sure that we have a partner from either of these methods
                if not partner_id.id:
                    _logger.error('We could not find a supplier using the provided VAT {vat} or GLN {gln}'.format(vat=str(document['Invoice']['sellerParty']['country']).upper() + document['Invoice']['sellerParty']['natTaxNo'], gln=document['Invoice']['sellerParty']['GLN']))
                    continue
                # We need to see if we can detect the currency
                currency_id = self.env['res.currency'].search([('name', '=', str(document['Invoice']['financialInfo']['currency']).upper())])
                # In case we do find a matching currency, we set the company base currency
                if not currency_id.id:
                    _logger.info('No valid currency was found. We tried to find {}'.format(str(document['Invoice']['financialInfo']['currency']).upper()))
                    currency_id = self.env.user.company_id.currency_id.id
                    
                # Now create the vendor bill
                vals = {
                    'partner_id': partner_id.id,
                    'user_id': self.env.user.id,
                    'reference': document['Invoice']['docID'],
                    # We have to create the bill correctly. So we check if the invoice value is negative or positive
                    'type': 'in_invoice' if document['Invoice']['documentTotals']['invoiceAmount'] > 0 else 'in_refund',
                    'date_invoice': document['Invoice']['docDate'],
                    'date_due': document['Invoice']['documentTotals']['dueDate'],
                    'currency_id': currency_id.id,
                    # We need to add this value so that know what document we have processed from the API
                    'edi_document_guid': val['conversationID'],
                    'edi_vendor_bill_total': document['Invoice']['documentTotals']['invoiceAmount'],
                    'edi_vendor_bill_total_untaxed': document['Invoice']['documentTotals']['vatBaseAmount']
                }
                vendor_bill = self.env['account.invoice'].create(vals)
                if vals['type'] == 'in_refund':
                    vals['edi_vendor_bill_total'] = vals['edi_vendor_bill_total'] * - \
                        1.0 if vals['edi_vendor_bill_total'] < 0 else vals['edi_vendor_bill_total']
                    vals['edi_vendor_bill_total_untaxed'] = vals['edi_vendor_bill_total_untaxed'] * - \
                        1.0 if vals['edi_vendor_bill_total_untaxed'] < 0 else vals['edi_vendor_bill_total_untaxed']
                # Handle refunds or invoices with invalid due dates
                if document['Invoice']['documentTotals']['dueDate'] == '0001-01-01T00:00:00' or '0001-01-01' in document['Invoice']['documentTotals']['dueDate']:
                    vals['date_due'] = document['Invoice']['docDate']
                # NOTE: Temp fix for cases where instance has oh_bankintegration module. This fix is removed once source module has been fixed
                if hasattr(self.env['account.invoice'], 'payment_duedate'):
                    vals['payment_duedate'] = vals['date_due']
                # Force a commit to the database
                self.env.cr.commit()

                # Update comment on vendor bill with payment details
                comment = ''
                # Add national bank payment details if we have them
                if document['Invoice']['paymentInfo']['paymBankReg'] and document['Invoice']['paymentInfo']['paymBankAcc']:
                    comment += "Reg: {reg} - Konto: {account} ".format(reg=document['Invoice']['paymentInfo']['paymBankReg'], account=document['Invoice']['paymentInfo']['paymBankAcc'])
                # International payment details if we have them
                if document['Invoice']['paymentInfo']['paymSwift'] and document['Invoice']['paymentInfo']['paymIBAN']:
                    comment += "Swift/BIC: {bic} - IBAN: {iban} ".format(bic=document['Invoice']['paymentInfo']['paymSwift'], iban=document['Invoice']['paymentInfo']['paymIBAN'])
                # Add Danish FI payment details if we have them
                if document['Invoice']['paymentInfo']['paymentID'] and document['Invoice']['paymentInfo']['paymTypeCode'] and document['Invoice']['paymentInfo']['paymCredGiro']:
                    comment += "Betal.ID +{code}<{paymentId}+{creditor}< ".format(code=document['Invoice']['paymentInfo']['paymTypeCode'], paymentId=document['Invoice']['paymentInfo']['paymentID'], creditor=document['Invoice']['paymentInfo']['paymCredGiro'])

                vendor_bill.update({
                    'comment': comment
                })
                # Force a commit to the database
                self.env.cr.commit()

                # DetailLines
                for line in document['Invoice']['DetailLines']:
                    l = None
                    product_id = self.env['product.product'].search(['|', ('default_code', '=', line['sellersItemNo']), ('default_code', '=', line['buyersItemNo'])])
                    name = line['description']
                    for comment in line['CommentLines']:
                        name += ' ' + comment['text']
                    default_values = self.env['account.invoice.line'].with_context(journal_id=vendor_bill.journal_id.id, type=vendor_bill.type).default_get([
                        'sequence',
                        'product_id',
                        'name',
                        'company_id',
                        'account_id',
                        'account_analytic_id',
                        'analytic_tag_ids',
                        'quantity',
                        'uom_id',
                        'price_unit',
                        'discount',
                        'invoice_line_tax_ids',
                        'price_subtotal',
                        'currency_id'
                    ])
                    _logger.info(default_values)
                    if product_id.id:
                        l = vendor_bill.invoice_line_ids.create({
                            'invoice_id': vendor_bill.id,
                            'product_id': product_id.id,
                            'name': name,
                            'price_unit': line['grossPrice'] if line['grossPrice'] > 0 and vendor_bill.type == 'in_refund' else line['grossPrice'] * -1.0,
                            'discount': line['discPct'],
                            'quantity': line['qtyTu'] if line['qtyTu'] > 0 and vendor_bill.type == 'in_refund' else line['qtyTu'] * -1.0,
                            'account_id': default_values.get('account_id', vendor_bill.journal_id.default_debit_account_id if vendor_bill.type not in ('out_invoice', 'in_refund') else vendor_bill.journal_id.default_credit_account_id)
                        })
                    else:
                        l = vendor_bill.invoice_line_ids.create({
                            'invoice_id': vendor_bill.id,
                            'name': name,
                            'price_unit': line['grossPrice'] if line['grossPrice'] > 0 and vendor_bill.type == 'in_refund' else line['grossPrice'] * -1.0,
                            'discount': line['discPct'],
                            'quantity': line['qtyTu'] if line['qtyTu'] > 0 and vendor_bill.type == 'in_refund' else line['qtyTu'] * -1.0,
                            'account_id': default_values.get('account_id', vendor_bill.journal_id.default_debit_account_id if vendor_bill.type not in ('out_invoice', 'in_refund') else vendor_bill.journal_id.default_credit_account_id)
                        })
                    # Force a commit to the database
                    self.env.cr.commit()
                    # Set correct taxes on the invoice line
                    l._set_taxes()
                    # Force a commit to the database
                    self.env.cr.commit()
                # AllowanceCharges - Things like addons or other things that are normally not invoice lines from other systems
                for line in document['Invoice']['AllowanceCharges']:
                    default_values = self.env['account.invoice.line'].with_context(journal_id=vendor_bill.journal_id.id, type=vendor_bill.type).default_get([
                        'sequence',
                        'product_id',
                        'name',
                        'company_id',
                        'account_id',
                        'account_analytic_id',
                        'analytic_tag_ids',
                        'quantity',
                        'uom_id',
                        'price_unit',
                        'discount',
                        'invoice_line_tax_ids',
                        'price_subtotal',
                        'currency_id'
                    ])
                    l = vendor_bill.invoice_line_ids.create({
                        'invoice_id': vendor_bill.id,
                        'name': line['allowanceChargeName'],
                        'price_unit': line['allowanceChargeAmount'],
                        'discount': 0,
                        'quantity': 1,
                        'account_id': default_values.get('account_id', vendor_bill.journal_id.default_debit_account_id if vendor_bill.type not in ('out_invoice', 'in_refund') else vendor_bill.journal_id.default_credit_account_id)
                    })
                    # Force a commit to the database
                    self.env.cr.commit()
                    # Set correct taxes on the invoice line
                    l._set_taxes()
                    # Force a commit to the database
                    self.env.cr.commit()
                
                # Once all lines are processed, we compute the taxes for the entire vendor bill
                vendor_bill.compute_taxes()
                # Force a commit to the database
                self.env.cr.commit()

                # Finally we inform the API, that weh have now processed the vendor bill
                # This we do only want to do when we run in production
                # If we debug an issue, we want to be able to process the same document
                # multiple times to fix any issue that might be there
                if self.env.user.company_id.edi_mode == 'production':
                    server_address = server_address + '/close'
                    # Here we return the database ID of the created vendor bill
                    # This is the only thing that we can do since the account.invoice.number record is not yet generated
                    result = requests.post(server_address, headers=headers, json={ 'Voucher': vendor_bill.id })
                    if not result.status_code == 200:
                        _logger.info('Error during request:')
                        _logger.info(result)
            else:
                _logger.info('This document is not an invoice')
