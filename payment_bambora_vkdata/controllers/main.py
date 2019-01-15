# -*- coding: utf-8 -*-


""" File to manage the functions used while redirection"""

import logging
import pprint
import werkzeug
from odoo import http, SUPERUSER_ID
from odoo.http import request

_logger = logging.getLogger(__name__)


class BamboraController(http.Controller):

    """ Handles the redirection back from payment gateway to merchant site """

    AcceptUrl = '/payment/bambora/accept/'
    CancelUrl = '/payment/bambora/cancel/'

    def _get_return_url(self, **post):
        """ Extract the return URL from the data coming from bambora. """
        return_url = post.pop('return_url', '')
        if not return_url:
            return_url = '/shop/payment/validate/'
        return return_url

    def bambora_validate_data(self, **post):
        """ Validate the data coming from bambora. """
        res = False
        reference = post['orderid']
        if reference:
            _logger.info('bambora: validated data')
            res = request.env['payment.transaction'].sudo().form_feedback(
                post, 'bambora_vkdata')
            return res

    @http.route('/payment/bambora/accept', type='http', auth='none',
                methods=['GET', 'POST'], csrf=False)
    def bambora_accept(self, **post):
        """ Gets the Post data from bambora after making payment """
        _logger.info('Beginning bambora Return form_feedback with post data %s',
                     pprint.pformat(post))  # debug
        return_url = self._get_return_url(**post)
        self.bambora_validate_data(**post)
        return werkzeug.utils.redirect(return_url)

    @http.route('/payment/bambora/cancel', type='http', auth="none", csrf=False)
    def bambora_cancel(self, **post):
        """ When the user cancels its bambora payment: GET on this route """
        _logger.info('Beginning bambora cancel with post data %s',
                     pprint.pformat(post))  # debug
        return_url = self._get_return_url(**post)
        return werkzeug.utils.redirect(return_url)
