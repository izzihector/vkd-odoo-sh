import paramiko
from datetime import datetime
from paramiko import SSHClient
from odoo.exceptions import ValidationError

from odoo import models, fields, api, _

import logging

_logger = logging.getLogger(__name__)

class OdooInstance(models.Model):
    _name = 'odoo.instance'
    _order = 'port_number'
    _inherit = ['mail.thread']


    active = fields.Boolean(default=True)
    display_name = fields.Char(help="The full domain name of the instance", compute='_set_full_domain_name', string="URL")

    # Basic information
    domain_name = fields.Char(string="Name", help="The name of the Odoo instance. For instances on dedicated servers, please use the full domain name.", required=True, track_visibility='always')
    primary_domain_name = fields.Char(help="The primary domain name of the instance. Use this field for dedicated instances, or to override the computed domain name.")
    description = fields.Text(track_visibility='always')
    purpose = fields.Selection([('demo', 'Demo'),
                                ('live', 'Live'),
                                ('trial', 'Trial'),
                                ('test', 'Test'),
                                ('development', 'Development'),
                                ('dedicated', 'Dedicated Live')], help="The purpose of this Odoo instance", required=True, track_visibility="always")
    customer_id = fields.Many2one('res.partner', string="Customer", track_visibility='always', help="Choose the customer this instance is for", required=True)
    subscription_id = fields.Many2one('sale.subscription', track_visibility='always', help="Choose the sales subscription relevant to this instance")
    request_user_id = fields.Many2one('hr.employee', string="Requested by", default=lambda self: self._get_employee(), track_visibility="always", help="The user that has requested the deployment of this instance")
    state = fields.Selection([('draft', 'Draft'),
                              ('queue', 'Queued'),
                              ('active', 'Active'),
                              ('to_suspend', 'To Suspend'),
                              ('suspend', 'Suspended'),
                              ('delete', 'To Delete'),
                              ('deleted', 'Deleted')],
                              help="The current status of the Odoo instance", default='draft', track_visibility="always")

    # Odoo information
    odoo_admin_username = fields.Char(string="Admin E-Mail", help="The initial username of the Odoo administrator", required=True, track_visibility='always')
    odoo_admin_password = fields.Char(string="Admin password", help="The initial password of the Odoo administrator", required=True, track_visibility='always')
    language_id = fields.Many2one('res.lang', domain="['|', ('active', '=', True), ('active', '=', False)]", required=True, track_visibility='always', help="The primary language used on this instance")
    version = fields.Selection([('10.0', '10.0'),
                                ('11.0', '11.0'),
                                ('12.0', '12.0')],
                                required=True, track_visibility="always")
    date_update = fields.Date(string="Last Updated", help="The date this Odoo instance was last updated.", track_visibility="onchange", default=datetime.today())
    
    # Technical information
    server_id = fields.Many2one('odoo.server', string="Server", track_visibility='always')
    linux_username = fields.Char(help="The username of the Linux system user running this Odoo instance. Used for SSH and SFTP.", track_visibility='always')
    linux_password = fields.Char(help="The password of the Linux system user running this Odoo instance Used for SSH and SFTP.", track_visibility='always')
    port_number = fields.Integer(help="The port number of this Odoo instance", required=True, track_visibility='always')
    longpolling_port_number = fields.Integer(help="The longpolling port number of this Odoo instance", track_visibility='always')
    ssl_certificate = fields.Boolean(string="Has SSL Certificate?", help="Check this if the instance has a valid SSL certificate")
    send_mail = fields.Boolean(default=False, help="Send an email to the address provided as the user e-mail, when the instance has been created")
    domain_ids = fields.One2many('odoo.instance.domains', 'instance_id', string="Domains", help="If there are additional domains attached to this instance, write them here.")
    database_admin_password = fields.Char(string="Database Admin Password", help="The password used for the Odoo database manager.", track_visibility='always')

    # Options
    community = fields.Boolean(help="Enable this if you want to deploy a community version")
    demo_data = fields.Boolean(help="Choose if this Odoo instance should have demo data installed", track_visibility='always')
    enable_website = fields.Boolean()
    enable_webshop = fields.Boolean()
    odoo_package = fields.Selection([('package_transport', 'Transport'),            # Package technical name
                                     ('package_detail', 'Detail'),
                                     ('package_production', 'Production')])

    website_theme = fields.Selection([('theme_wine', 'Wine Theme'),         # Theme techical name
                                      ('theme_other', 'Another Theme')])

    ##################
    ##  CONSTRAINS  ##
    ##################

    @api.constrains('domain_name')
    def check_domain_name(self):
        instances = self.env['odoo.instance'].search([('server_id', '=', self.server_id.id),
                                                      ('domain_name', '=', self.domain_name),
                                                      ('active', '=', True),
                                                      ('id', '!=', self.id)])
        if len(instances.ids) > 0:
            raise ValidationError(_('Error! There is already an active instance with the given name on the chosen server'))

    @api.constrains('port_number')
    def check_port_number(self):
        instances = self.env['odoo.instance'].search([('server_id', '=', self.server_id.id),
                                                      ('port_number', '=', self.port_number),
                                                      ('active', '=', True),
                                                      ('id', '!=', self.id)])
        if len(instances.ids) > 0:
            raise ValidationError(_('Error! There is already an active instance with the designated portnumber on the chosen server'))

    @api.constrains('server_id')
    def check_server_id(self):
        if not self.server_id:
            raise ValidationError(_('Error! Server not correctly assigned. Please contact technical support'))
    
    ##################
    ##   ACTIONS    ##
    ##################

    @api.multi
    def action_set_to_suspend(self):
        for r in self:
            r.state = 'to_suspend'

    @api.multi
    def action_set_to_delete(self):
        for r in self:
            r.state = 'delete'

    @api.model
    def create(self, vals):
        instance = super(OdooInstance, self).create(vals)

        security_group_ids = self.env.ref('automatic_odoo_deployment.group_instance_admin').ids
        users = self.env['res.users'].search([('groups_id', 'in', security_group_ids),('id', '!=', self.env.ref('base.user_root').id)]).ids
        if instance.request_user_id.user_id:
            users.append(instance.request_user_id.user_id.id)

        instance.message_subscribe_users(user_ids=users)

        return instance

    ##################
    ##   COMPUTED   ##
    ##################

    @api.depends('domain_name', 'server_id.cluster_id.dns_suffix', 'purpose', 'primary_domain_name')
    def _set_full_domain_name(self):
        for r in self:
            prefix = "http://"
            if r.ssl_certificate:
                prefix = "https://"
                
            if r.primary_domain_name:
                r.display_name = prefix + r.primary_domain_name
            elif r.domain_name and r.server_id and r.purpose != 'dedicated':
                suffix = r.server_id.cluster_id.dns_suffix if r.server_id.cluster_id.dns_suffix[0] == '.' else '.' + r.server_id.cluster_id.dns_suffix
                r.display_name = prefix + r.domain_name + suffix
            elif r.domain_name:
                r.display_name = prefix + r.domain_name
            else:
                r.display_name = ''

    def _get_employee(self):
        try:
            employee_id = self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1).id
            return employee_id
        except Exception as e:
            _logger.info(e)
            return None

    ##################
    ##   ONCHANGE   ##
    ##################

    @api.onchange('purpose')
    def _set_linux_user(self):
        if self.purpose != 'dedicated':
            self.linux_username = self.domain_name
        else:
            self.linux_username = ''

    @api.onchange('purpose')
    def _set_server_id(self):
        if self.purpose == 'dedicated':
            server = self.env['odoo.server'].search([('name', 'ilike', self.domain_name)])
            if server:
                self.server_id = server.id
            else:
                self.server_id = False
        else:
            cluster = self.env['odoo.cluster'].search([('purpose', '=', self.purpose)])
            servers = cluster.server_ids
            load_balance = self.env['ir.config_parameter'].sudo().get_param('automatic_odoo_deployment.use_load_balancing')
            if load_balance:
                servers = servers.sorted(key=lambda r: len(r.instance_ids), reverse=True)
            for server in servers:
                if server.max_instances == -1:
                    self.server_id = server.id
                elif len(server.instance_ids) >= server.max_instances:
                    pass
                elif len(server.instance_ids) < server.max_instances:
                    self.server_id = server.id

    @api.onchange('server_id')
    def _set_ssl_enabled(self):
        if self.server_id and self.server_id.ssl_certificate:
            self.ssl_certificate = True
        else:
            self.ssl_certificate = False

    @api.onchange('server_id')
    def _set_port_number(self):
        if self.purpose == 'dedicated':
            self.port_number = 8069
            self.longpolling_port_number = 8072
        else:
            instances = self.env['odoo.instance'].search([('server_id.id', '=', self.server_id.id)])
            for instance in (x for x in instances if x.state != 'deleted'):
                if instance.port_number == self.port_number:
                    self.port_number += 2
            self.longpolling_port_number = self.port_number + 1
    
    ##################
    ##  DEPLOYMENT  ##
    ##################

    def update_instance(self):
        _logger.info('Updating instance')
        client = SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.load_system_host_keys()
        client.connect(self.server_id.ip_address, username=self.server_id.admin_username, password=self.server_id.admin_password)

        command = "sudo bash /opt/tools/update-odoo11.sh '{0}'".format(self.linux_username)
        stdin, stdout, stderr = client.exec_command(command)
        stdout.channel.recv_exit_status()

        _logger.info('Instance has been updated')


    def shut_down_instance(self):
        _logger.info('Starting instance shutdown')
        client = SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.load_system_host_keys()
        client.connect(self.server_id.ip_address, username=self.server_id.admin_username, password=self.server_id.admin_password)

        command = "sudo systemctl stop {0}-odoo".format(self.linux_username)
        stdin, stdout, stderr = client.exec_command(command)
        stdout.channel.recv_exit_status()

        command = "sudo systemctl disable {0}-odoo".format(self.linux_username)
        stdin, stdout, stderr = client.exec_command(command)
        stdout.channel.recv_exit_status()

        _logger.info('Instance has been shut down')
        self.state = 'suspend'

    def start_instance(self):
        _logger.info('Starting up instance')
        client = SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.load_system_host_keys()
        client.connect(self.server_id.ip_address, username=self.server_id.admin_username, password=self.server_id.admin_password)

        command = "sudo systemctl enable {0}-odoo".format(self.linux_username)
        stdin, stdout, stderr = client.exec_command(command)
        stdout.channel.recv_exit_status()

        command = "sudo systemctl start {0}-odoo".format(self.linux_username)
        stdin, stdout, stderr = client.exec_command(command)
        stdout.channel.recv_exit_status()

        _logger.info('Instance has been started')
        self.state = 'active'


    def terminate_instance(self):
        _logger.info('Terminating instance')
        client = SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.load_system_host_keys()
        client.connect(self.server_id.ip_address, username=self.server_id.admin_username, password=self.server_id.admin_password)

        command = "sudo bash /opt/tools/terminate-odoo.sh '{0}' '{1}'".format(self.linux_username, self.display_name)
        stdin, stdout, stderr = client.exec_command(command)
        stdout.channel.recv_exit_status()

        _logger.info('Instance has been terminated')
        self.unlink()

    def remote_deploy(self):
        # stdout.channel.recv_exit_status() makes sure the remote process is finished before continuing
        _logger.info('Starting deployment')
        client = SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.load_system_host_keys()
        client.connect(self.server_id.ip_address, username=self.server_id.admin_username, password=self.server_id.admin_password)
        _logger.info('Connected to remote server')
        command = "sudo bash /opt/tools/deploy-odoo11.sh '{0}' '{1}' {2} {3}".format(self.linux_username, self.domain_name + self.server_id.cluster_id.dns_suffix, self.port_number, self.longpolling_port_number)
        if self.community:
            command += ' "community"'
        stdin, stdout, stderr = client.exec_command(command)
        output = stdout.readlines()
        for line in output:
            if 'Password: ' in line:
                self.linux_password = line.split(": ")[-1]

        stdout.channel.recv_exit_status()
        _logger.info('Succesfully deployed new instance')

        if self.language.code == 'da_DK' and not self.demo_data:
            command = 'sudo git clone git@github.com:vkdata/l10n_dk.git /home/{0}/odoo/custom/'.format(self.linux_username)
            stdin, stdout, stderr = client.exec_command(command)
            stdout.channel.recv_exit_status()
            _logger.info('Cloned danish chart of accounts')

        module_list = []
        if self.odoo_package:
            module_list.append(self.odoo_package)
            command = 'sudo git clone git@github.com:vkdata/package-installers.git /home/{0}/odoo/custom'.format(self.linux_username)
            stdin, stdout, stderr = client.exec_command(command)
            stdout.channel.recv_exit_status()

        if self.enable_website:
            module_list.append('website')
            _logger.info('Added website to module list')
            if self.enable_webshop:
                module_list.append('website_sale')
                _logger.info('Added website_sale to module list')
            if self.website_theme:
                module_list.append(self.website_theme)
                command = 'sudo git clone git@github.com:vkdata/odoo-themes.git /home/{0}/odoo/custom'.format(self.linux_username)
                stdin, stdout, stderr = client.exec_command(command)
                stdout.channel.recv_exit_status()

        command = 'sudo chown {0}:{0} /home/{0}'.format(self.linux_username)
        stdin, stdout, stderr = client.exec_command(command)
        stdout.channel.recv_exit_status()
       
        command = "sudo python3 /opt/tools/odoo_create_db.py '{0}' '{1}' '{2}' '{3}' '{4}' '{5}' '{6}'".format('#VKD978p', self.linux_username, self.demo_data, self.language.code, self.odoo_admin_password, self.port_number, self.odoo_admin_username)
        stdin, stdout, stderr = client.exec_command(command)
        stdout.channel.recv_exit_status()

        _logger.info('Created db')
        for mod in module_list:
            command = "sudo python3 /opt/tools/odoo_install_modules.py '{0}' '{1}' '{2}' '{3}' '{4}'".format(self.port_number, self.odoo_admin_username, self.odoo_admin_password, self.linux_username, mod)
            stdin, stdout, stderr = client.exec_command(command)
            stdout.channel.recv_exit_status()
            _logger.info('Installed module: %s', mod)
        
        client.close()

        self.state = 'active'
        _logger.info('Deployment done!')
        # if self.send_mail:
        #     self.send_email()