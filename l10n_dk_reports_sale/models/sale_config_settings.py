from odoo import models, fields, api
import logging
_logger = logging.getLogger(__name__)


class AccountInvoiceReport(models.Model):
    _inherit = "account.invoice"
    sale_address_option = fields.Char(compute='_sale_config_option_to_report')

    def _sale_config_option_to_report(self):
        #company_id = self.company_id.id
        sale_settings = self.env['sale.config.settings'].search([])[-1]
        for s in sale_settings:
            _logger.info('%s - %s', s.group_sale_delivery_address, s.company_id)
        self.sale_address_option = sale_settings.group_sale_delivery_address
        #_logger.info('%s', sale_settings.group_sale_delivery_address)
