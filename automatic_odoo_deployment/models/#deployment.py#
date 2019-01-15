
from odoo import models, fields, api

# Model for running cron jobs
class InstanceManager(models.AbstractModel):
    _name = 'instance.manager'

    def process_creation_queue(self):
        instances = self.env['odoo.instance'].search([('state', '=', 'queue')])
        for instance in instances:
            instance.remote_deploy()
