# -*- coding: utf-8 -*-
from odoo import models, fields, api


class OdooEdiEndpoint(models.Model):
    _name = 'odoo_edi.endpoint'
    _description = 'Odoo EDI Endpoint Definition'

    document_type_id = fields.Char(string="Document Type ID")
    name = fields.Char(string="Endpoint Id")
    description = fields.Char(string="Endpoint name")

    display_name = fields.Char(compute="_compute_display_name")

    #_sql_constraints = [
    #    ('name_uniq', 'unique (name)', 'The name must be unique !')
    #]

    def _compute_display_name(self):
        for endpoint in self:
            endpoint.display_name = endpoint.name + \
                ' (' + endpoint.description + ')'
