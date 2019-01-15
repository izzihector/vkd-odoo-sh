# -*- coding: utf-8 -*-
import sys
import base64
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from dateutil.parser import parse
import logging
import re
from decimal import Decimal
import csv
from io import StringIO
import datetime
_logger = logging.getLogger(__name__)


class AccountBankStatementImport(models.TransientModel):
    _name = 'account.bank.statement.import'
    _inherit = "account.bank.statement.import"

    # Function to if two float values are same or not
    def isClose(self, a, b, rel_tol=1e-09, abs_tol=0.0):
        return abs(a - b) <= max(rel_tol * max(abs(a), abs(b)), abs_tol)

    @api.multi
    def bankintegration_import_statements(self, currency_code, account_number, stmts_vals):
        """ Process the statements captured using bankintegration API. """
        #self.ensure_one()
        # Check raw data
        self._check_parsed_data(stmts_vals)
        # Try to find the currency and journal in odoo
        currency, journal = self._find_additional_data(currency_code, account_number)
        # If no journal found, ask the user about creating one
        if not journal:
            # The active_id is passed in context so the wizard can call import_file again once the journal is created
            return self.with_context(active_id=self.ids[0])._journal_creation_wizard(currency, account_number)
        if not journal.default_debit_account_id or not journal.default_credit_account_id:
            raise UserError(_('You have to set a Default Debit Account and a Default Credit Account for the journal: %s') % (journal.name,))
        # Prepare statement data to be used for bank statements creation
        stmts_vals = self._complete_stmts_vals(stmts_vals, journal, account_number)
        # Create the bank statements
        statement_ids, notifications = self._create_bank_statements(stmts_vals)
        # Now that the import worked out, set it as the bank_statements_source of the journal
        journal.bank_statements_source = 'bankintegration_import'
        # Finally dispatch to reconciliation interface
        action = self.env.ref('account.action_bank_reconcile_bank_statements')
        return {
            'name': action.name,
            'tag': action.tag,
            'context': {
                'statement_ids': statement_ids,
                'notifications': notifications
            },
            'type': 'ir.actions.client',
        }
