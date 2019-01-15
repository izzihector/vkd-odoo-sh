import math
from odoo import models, fields, api
import logging
_logger = logging.getLogger(__name__)

class AccountInvoice(models.Model):
    _inherit = "account.invoice"
    fik_line = fields.Char(compute='_compute_fik_line')

    def digits_of(self, number):
        return [int(i) for i in str(number)]

    def luhn_checksum(self, card_number):
        digits = self.digits_of(card_number)
        odd_digits = digits[-1::-2]
        even_digits = digits[-2::-2]
        total = sum(odd_digits)
        for digit in even_digits:
            total += sum(self.digits_of(2 * digit))
        return total % 10

    def calculate_luhn(self, partial_card_number):
        check_digit = self.luhn_checksum(int(partial_card_number) * 10)
        if check_digit == 0:
            return check_digit
        else:
            return 10 - check_digit

    #def FIKfi(self, str, vagt):
    #    sum = str * vagt
    #    if sum > 9:
    #        sum = math.fmod(float(sum), 10) + math.floor(float(sum) / 10)
    #        return sum

    #def FIK(self, str):
    #    telsum = 0
    #    for i in range(0, len(str) - 1):
    #        if (math.fmod(i + 1, 2) == 0):
    #            telsum = telsum + self.FIKfi(2, str[i])
    #        else:
    #            telsum = telsum + self.FIKfi(1, str[i])
    #    checktal = (10 - (math.fmod(telsum, 10)))
    #    if math.fmod(telsum, 10) == 0:
    #        return 0
    #    else:
    #        return checktal

    def _compute_fik_line(self):
        for r in self:
            company_id = r.company_id.id
            account_settings = r.env['res.company'].search([('id', '=', company_id)])

            if not account_settings.fik_enabled:
                return None
            if not r.number:
                _logger.info(' No invoice number defined ')
                return None
            elif not account_settings.invoice_prefix:
                _logger.info(' No invoice prefix defined in the accounting configuration settings ')
                return None
            elif not r.number.replace(account_settings.invoice_prefix, "").isdigit():
                _logger.info(' The invoice number %s contains invalid characters. Please make sure that you have defined the same prefix of the sequence and the invoice prefix in the acccounting configuration', r.number)
                return None
            elif not account_settings.fik_settings:
                _logger.info(' No fik line configuration found ')
                return None
            elif not account_settings.fik_id:
                _logger.info(' No fik number defined in the accounting configuration settings ')
                return None

            commercial_partner_id = r.commercial_partner_id.ref
            invoice_number = r.number.replace(account_settings.invoice_prefix, "")
            customer_code_length = account_settings.fik_settings.customer_code_length
            invoice_number_length = account_settings.fik_settings.invoice_number_length

            if invoice_number_length == 0:
                invoice_number = ""
            if customer_code_length == 0:
                commercial_partner_id = ""
            if not commercial_partner_id:
                commercial_partner_id = ""
            if len(invoice_number) > invoice_number_length:
                invoice_number = invoice_number[-invoice_number_length:]
            if len(commercial_partner_id) > customer_code_length:
                commercial_partner_id = commercial_partner_id[:customer_code_length]
            if len(invoice_number) < invoice_number_length:
                for i in range(len(invoice_number), invoice_number_length):
                    invoice_number = "0" + invoice_number
            if len(commercial_partner_id) < customer_code_length:
                for i in range(len(commercial_partner_id), customer_code_length):
                    commercial_partner_id = "0" + commercial_partner_id

            fikstring = commercial_partner_id + invoice_number
            r.fik_line = "+71<" + fikstring + str(int(r.calculate_luhn(fikstring))) + "+" + account_settings.fik_id + "<"
