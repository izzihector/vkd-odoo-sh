# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import api, fields, models


class account_journal(models.Model):
    _inherit = "account.journal"

    @api.multi
    def import_csv_statement(self):
        action = self.env.ref('import_csv_statement.action_import_csv_statement').read()[0]
        action.update({
            'context': "{'default_journal_id': " + str(self.id) + "}",
        })
        return action


class Bank(models.Model):
    _inherit = "res.bank"

    date_header = fields.Char(help="Give the column name of the field containing the posting date")
    amount_header = fields.Char(help="Give the column name of the field containing the posting amount in the base currency")
    refernce_header = fields.Char(help="Give the column name of the field containing the posting text/label")
    foreign_amount_header = fields.Char(help="Give the column name of the field containing the amount in foreign currency")
    foreign_currency_header = fields.Char(help="Give the column name of the field containing the name of the foreign currency")
    date_format = fields.Char(help="Here you can input the date format used for the posting date. For Danske Bank type 1, for Nordea type 2, for BankData (Kreditbanken, Jyske Bank etc.) type 3. For anyone else, please specify the full date format")
    skip_last_line = fields.Boolean(string="Skip last line of the file", help="Check this if the last line of the CSV file should not be imported. This must be checked if your bank used BankData as their service provider")
