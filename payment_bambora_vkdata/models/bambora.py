# -*- coding: utf-8 -*-



""" This file manages all the operations and the functionality of the gateway
integration """

import json
import logging
import re
from werkzeug import urls
from urllib.request import urlopen
from urllib.parse import urljoin
from odoo import http
from odoo.http import request
from odoo.addons.payment.models.payment_acquirer import ValidationError
from odoo.addons.payment_bambora_vkdata.controllers.main import BamboraController
from odoo import fields, models
from openerp.tools.translate import _

_logger = logging.getLogger(__name__)


class AcquirerBambora(models.Model):

    """ Class to handle all the functions required in integration """
    _inherit = 'payment.acquirer'

    def _get_bambora_urls(self, environment):
        """ Bambora URLS """
        if environment == 'prod':
            return {
                'bambora_form_url':
                    'https://ssl.ditonlinebetalingssystem.dk/integration/ewindow/'
                    'Default.aspx',
            }
        else:
            return {
                'bambora_form_url':
                    'https://ssl.ditonlinebetalingssystem.dk/integration/ewindow'
                    '/Default.aspx',
            }

    provider = fields.Selection(selection_add=[('bambora_vkdata',
                                                'Bambora')])
    bambora_merchant_number = fields.Char('Bambora Merchant Number',
                                          required_if_provider='bambora_vkdata')

    def bambora_vkdata_form_generate_values(self, values):
        """ Gathers the data required to make payment """
        #base_url = self.env['ir.config_parameter'].get_param('web.base.url')

        url = str(http.request.httprequest)
        #urls = re.findall('http?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', url)
        #parsed_uri = urlopen(urls[0])
        base_url = self.env['ir.config_parameter'].get_param('web.base.url')
		
		
        bambora_tx_values = dict(values)
        bambora_tx_values.update({
            'merchantnumber': self.bambora_merchant_number,
			#'merchantnumber': 8032334,
            'currency': values['currency'] and values['currency'].name or '',
            'amount': str(int(values['amount'] * 100)) or '',
            'orderid': values['reference'] or '',
            'windowstate': '3',
            'instantcapture': '1',
            'accepturl': '%s' % urljoin(base_url, BamboraController.AcceptUrl),
            'cancelurl': '%s' % urljoin
            (base_url, BamboraController.CancelUrl),
            'custom':
            json.dumps({'return_url':
                        '%s' % bambora_tx_values.pop('return_url')}
                        ) if bambora_tx_values.get('return_url') else False,
        })
        return bambora_tx_values

    def bambora_vkdata_get_form_action_url(self):
        """ Gets the Url of the payment form of bambora """
        return self._get_bambora_urls(self.environment)['bambora_form_url']


class TxBambora(models.Model):

    """ Handles the functions for validation after transaction is processed """
    _inherit = 'payment.transaction'

    # --------------------------------------------------
    # FORM RELATED METHODS
    # --------------------------------------------------

    def _bambora_vkdata_form_get_tx_from_data(self, data):
        """ Given a data dict coming from bambora, verify it and find '
        'the related transaction record. Create a payment method if '
        'an alias is returned."""

        if data['txnid']:
            reference = data.get('orderid')
            if not reference:
                error_msg = _(
                    'Bambora: received data with missing reference (%s)'
                ) % (reference)
                _logger.info(error_msg)
                raise ValidationError(error_msg)

            tx_ids = self.env['payment.transaction'
                                ].search([('reference', '=', reference)])
            if not tx_ids or len(tx_ids) > 1:
                error_msg = 'Bambora: received data for reference %s' % (
                    reference)
                if not tx_ids:
                    error_msg += '; no order found'
                else:
                    error_msg += '; multiple order found'
                _logger.info(error_msg)
                raise ValidationError(error_msg)
            return tx_ids[0]

    def _bambora_vkdata_form_validate(self, data):
        """ Verify the validity of data coming from bambora"""
        res = {}
        if data['txnid']:
            _logger.info(
                'Validated Bambora payment for tx %s: set as '
                'done' % (self.reference))
            res.update(state='done', date_validate=data.get(
                'payment_date', fields.datetime.now()))
            return self.write(res)
        else:
            error = 'Received unrecognized data for Bambora payment %s,' \
                ' set as error' % (self.reference)
            _logger.info(error)
            res.update(state='error', state_message=error)
            self.write(res)
