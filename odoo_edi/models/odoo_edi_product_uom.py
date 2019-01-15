# -*- coding: utf-8 -*-
from odoo import models, fields, api


class OdooEdiProductUom(models.Model):
    _name = 'odoo_edi.product.uom'
    _description = 'EDI standard Unit of measure name'

    name = fields.Char(string="EDI unit name")
    description = fields.Char(string="EDI unit description")

    display_name = fields.Char(compute="_compute_display_name")

    #_sql_constraints = [
    #    ('name_uniq', 'unique (name)', 'The name must be unique !')
    #]

    def _compute_display_name(self):
        for uom in self:
            uom.display_name = uom.name + ' (' + uom.description + ')'
