# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import base64
import csv
from datetime import datetime
import logging

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT

_logger = logging.getLogger(__name__)

from io import StringIO
from io import BytesIO


class ImportCSVStatement(models.TransientModel):
    _name = 'import.csv.statement'

    journal_id = fields.Many2one('account.journal', string="Bank", domain=[('type', '=', 'bank')], required=True)
    statement_id = fields.Many2one('account.bank.statement', string="Statement", required=True)
    data_file = fields.Binary(string='Price File', required=True)
    filename = fields.Char()

    def _format_date(self, date,date_format):
        # This is the format for Danske Bank
        if date_format == '1':
            return datetime.strptime(date, '%d.%m.%Y').strftime(DEFAULT_SERVER_DATE_FORMAT)
        # This is the format for Nordea
        if date_format == '2':
            date_str = datetime.strptime(date,'%Y.%m.%d').strftime('%d.%m.%Y')
            return datetime.strptime(date_str, '%d.%m.%Y').strftime(DEFAULT_SERVER_DATE_FORMAT)
        # This is the format for BankData
        if date_format == '3':
            return datetime.strptime(date, '%d-%m-%Y').strftime(DEFAULT_SERVER_DATE_FORMAT)
        else:
            return datetime.strptime(date, date_format).strftime(DEFAULT_SERVER_DATE_FORMAT)


    def _create_bank_statment(self, datas):
        AccountInvoice = self.env['account.invoice']
        ResPartner = self.env['res.partner']
        ResCurrency = self.env['res.currency']
        lines = []
        date_header = self.journal_id.bank_id.date_header.encode('cp1252', 'ignore').decode('cp1252', 'ignore')
        amount_header = self.journal_id.bank_id.amount_header.encode(
            'cp1252', 'ignore').decode('cp1252', 'ignore')
        foreign_currency_header = None
        foreign_amount_header = None
        if self.journal_id.bank_id.foreign_amount_header:
            foreign_amount_header = self.journal_id.bank_id.foreign_amount_header.encode(
                'cp1252', 'ignore').decode('cp1252', 'ignore')
        if self.journal_id.bank_id.foreign_currency_header:
            foreign_currency_header = self.journal_id.bank_id.foreign_currency_header.encode(
                'cp1252', 'ignore').decode('cp1252', 'ignore')
        refernce_header = self.journal_id.bank_id.refernce_header.encode('cp1252', 'ignore').decode('cp1252', 'ignore')
        date_format = self.journal_id.bank_id.date_format.encode(
            'cp1252', 'ignore').decode('cp1252', 'ignore')
        skip_last_line = self.journal_id.bank_id.skip_last_line
        if date_header == '' or amount_header == '' or refernce_header == '':
            raise UserError(_('Please Configure CSV Headers In Bank View.'))
        try:
            if skip_last_line:
                datas.pop()
            
            for data in datas:
                date = self._format_date(data.get(date_header), date_format)

                name = data.get(refernce_header)
                amount = data.get(amount_header).replace(',', '.')

                partner_id = False
                for code in name.split():
                    if code.isdigit():
                        invoice = AccountInvoice.search([('name', '=', code)]).partner_id.id
                        partner_id = invoice[0].partner_id.id if invoice else False
                    if not partner_id:
                        partner = ResPartner.search([('ref', '=', code)])
                        partner_id = partner[0].id if partner else False
                vals = {
                    'date': date,
                    'name': name,
                    'amount': amount,
                    'partner_id': partner_id
                }
                if foreign_currency_header and data.get(foreign_currency_header):
                    vals.update({ 'currency_id' : ResCurrency.search([('name', '=', data.get(foreign_currency_header))])[0].id })
                if foreign_amount_header and not data.get(foreign_amount_header) == '0,00':
                    if ' ' in vals['amount']:
                        vals['amount'].replace(' ', '')
                    if float(vals['amount']) < 0.0 and float(data.get(foreign_amount_header).replace(',', '.')) > 0.0:
                        vals.update({'amount_currency' : "-" + data.get(foreign_amount_header).replace(',','.').replace(' ', '')})
                    else:
                        vals.update({'amount_currency' : data.get(foreign_amount_header).replace(',','.').replace(' ', '')})
                lines.append((0, 0, vals))

            if self.statement_id:
               self.statement_id.write({'line_ids': lines})
            return True
        except Exception as e:
            print("eeeee", e)
            _logger.info(e)
            raise UserError(_('Something wrong in csv file please check your csv file.'))

    @api.multi
    def import_file(self):
        self.ensure_one()
        if not self.filename.endswith('.csv') and not self.filename.endswith('.CSV'):
            raise UserError(_('Only csv file format is supported to import file'))
        data = csv.reader(StringIO(BytesIO(base64.b64decode(self.data_file)).read().decode('cp1252', 'ignore')), quotechar='"', delimiter=';')
        # Read the column names from the first line of the file

        fields = [x.replace('"', '') for x in next(data)]

        datas = []
        for row in data:
            items = dict(zip(fields, row))
            datas.append(items)
        return self._create_bank_statment(datas)

