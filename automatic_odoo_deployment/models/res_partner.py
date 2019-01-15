from odoo import models, fields, api, _

class ResPartner(models.Model):
    _inherit = 'res.partner'

    instance_ids = fields.One2many('odoo.instance', 'customer_id')
    instance_count = fields.Integer(compute="calc_instance_ids")

    def calc_instance_ids(self):
        results = self.env['odoo.instance'].read_group([('customer_id', 'in', self.ids)], 'customer_id', 'customer_id')

        instances = {}

        for res in results:
            instances[res['customer_id'][0]] = res['customer_id_count']

        for record in self:
            record['instance_count'] = instances.get(record.id, 0)