# See LICENSE file for full copyright and licensing details.
import json

from odoo import models, api, fields

EP_IsSyncedWithOdoo = 'Integer {ada9f591-5bb3-42c6-b79f-21895dc019a2} Name IsSyncedWithOdoo'
EP_ResPartnerId = 'Integer {ada9f941-5bb3-42c6-b79f-21895dc019a2} Name ResPartnerId'


class ResPartner(models.Model):
    _name = 'res.partner'
    _inherit = ['res.partner', 'azure.ad.change.queuer']

    contact_sync_use_category = fields.Boolean(string='Only Sync Contacts With Category', related='azure_ad_user_id.contact_sync_use_category')
    contact_sync_filter_options = fields.Selection(string='Contacts to Sync', related='azure_ad_user_id.contact_sync_filter_options')
    contact_sync_filters = fields.Many2many(string='Filters', related='azure_ad_user_id.contact_sync_filters')

    outlook_categories = fields.Char('Categories from Outlook')

    def get_to_sync_contact_list(self):
        """Returns the Contacts that should be synced in an Array of Objects"""
        data = []

        if self.contact_sync_filter_options == 'all':
            res_partner_list = self.search([])
        elif self.contact_sync_filter_options == 'filter':
            user_id = self.env['res.users'].search([('partner_id', '=', self.id)])

            res_partner_list = self.contact_sync_filters.get_filtered_partners_for_user(user_id)

        for partner in res_partner_list:
            data.append(('res.partner,%d' % partner['id'], partner.get_azure_ad_contact()))

        return data

    # --------------
    # CRUD Overrides
    # --------------
    @api.model
    def create(self, vals):
        partner = super(ResPartner, self).create(vals)

        users = partner.get_azure_ad_to_sync_users()
        contact = partner.get_azure_ad_contact()

        users.create_contacts(contacts=[('res.partner,%d' % partner['id'], contact)])

        return partner

    # ------------------
    # Abstract Overrides
    # ------------------
    @api.multi
    def prepare_azure_ad_template(self, change, is_child=False):
        return self.prepare_contact_template(dict_fields=change, company_fields_only=is_child)

    @api.model
    def get_change_observed_values(self):
        return ['name', 'title', 'email', 'function', 'parent_id', 'phone', 'mobile', 'street', 'street2', 'city', 'state_id', 'country_id', 'zip', 'id', 'outlook_categories']

    # ------------
    # Data Parsers
    # ------------
    @api.model
    def extract_contact_fields(self, contact):
        name = contact[u'DisplayName'][len(contact[u'Title']) + 1:] if contact[u'Title'] and contact[u'DisplayName'].startswith(contact[u'Title']) else contact[u'DisplayName']
        title = None

        if contact[u'Title']:
            title_options = self.env['res.partner.title'].search([('name', '=', contact[u'Title'])])
            title = title_options.id if title_options else None

            if not title:
                name = '%s %s' % (contact[u'Title'], name)

        values = {
            'name': name,
            'title': title,
            'email': contact[u'EmailAddresses'][0][u'Address'] if len(contact[u'EmailAddresses']) and u'Address' in contact[u'EmailAddresses'][0] else '',
            'function': contact[u'JobTitle'],
            'phone': contact[u'BusinessPhones'][0] if contact[u'BusinessPhones'] else None,
            'mobile': contact[u'MobilePhone1'],
            'outlook_categories': json.dumps(contact[u'Categories']),
        }

        if contact[u'BusinessAddress']:
            address = contact[u'BusinessAddress']

            values['street'] = address[u'Street'] if u'Street' in address else None
            values['city'] = address[u'City'] if u'City' in address else None
            values['zip'] = address[u'PostalCode'] if u'PostalCode' in address else None

            # TODO Match state/country
            # values['state_id/name'] = address[u'State'] if u'State' in address else None,
            # values['country_id/name'] = address[u'CountryOrRegion'] if u'CountryOrRegion' in address else None,

        return {k: v for k, v in values.items() if v is not None}

    @api.multi
    def get_azure_ad_contact(self):
        self.ensure_one()

        values = {
            'name': self.name,
            'title': self.title,
            'email': self.email,
            'function': self.function,
            'parent_id': self.parent_id,
            'phone': self.phone,
            'mobile': self.mobile,
            'street': self.street,
            'street2': self.street2,
            'city': self.city,
            'state_id': self.state_id,
            'country_id': self.country_id,
            'zip': self.zip,
            'id': self.id,
            'outlook_categories': self.outlook_categories,
        }

        template = self.prepare_contact_template({k: v for k, v in values.items() if v}, True)
        extra_values = self.get_extra_custom_values()

        if extra_values:
            template = self.merge_values(template, extra_values)

        return template

    @api.multi
    def prepare_contact_template(self, dict_fields, new=False, company_fields_only=False):
        main_level_fields = {'GivenName': 'name', 'Title': 'title/name', 'JobTitle': 'function', 'CompanyName': 'parent_id/name', 'MobilePhone1': 'mobile'}
        email_level_fields = {'Address': 'email', 'Name': 'name'}
        address_level_fields = {'Street': 'street+street2', 'City': 'city', 'State': 'state_id/name', 'CountryOrRegion': 'country_id/name', 'PostalCode': 'zip'}

        if not company_fields_only:
            contact = self.dict_creator(main_level_fields, dict_fields)
            email_level_dict = self.dict_creator(email_level_fields, dict_fields)

            if 'GivenName' in contact:
                contact['Surname'] = ''
                contact['MiddleName'] = ''

            if len(email_level_dict):
                email_level_dict.setdefault('Address', self.email or '')
                email_level_dict.setdefault('Name', self.name or '')

                contact['EmailAddresses'] = [email_level_dict]

            if 'phone' in dict_fields:
                contact['BusinessPhones'] = [dict_fields['phone']]
        else:
            contact = {'CompanyName': dict_fields['name']} if 'name' in dict_fields else {}

        address_level_dict = self.dict_creator(address_level_fields, dict_fields, contain_all=True)

        if len(address_level_dict):
            contact['BusinessAddress'] = address_level_dict

        if new:
            contact['FileAs'] = "%s %s" % (contact['GivenName'] if 'GivenName' in contact else '', "(%s)" % contact['CompanyName'] if 'CompanyName' in contact else '')
            contact['SingleValueExtendedProperties'] = [{
                'PropertyId': EP_IsSyncedWithOdoo,
                'Value': '1'
            }, {
                'PropertyId': EP_ResPartnerId,
                'Value': str(self.id)
            }]

        if 'outlook_categories' in dict_fields and dict_fields['outlook_categories']:
            contact['Categories'] = json.loads(dict_fields['outlook_categories'])

        return contact

    @api.multi
    def dict_creator(self, field_dict, value_dict, contain_all=False):
        d = {}

        for k, v in field_dict.items():
            option_fields = [option.split('/') for option in v.split('+')]
            val = None

            for option in option_fields:
                if option[0] in value_dict or contain_all:
                    s = self[option[0]][option[1]] if len(option) == 2 else value_dict[option[0]] if option[0] in value_dict else self[option[0]]

                    if val is None:
                        val = s if s else None
                    else:
                        try:
                            val += ' ' + s
                        except TypeError:
                            pass

            if val is not None:
                d[k] = str(val)

        return d

    # -------
    # Helpers
    # -------
    @api.multi
    def get_azure_ad_to_sync_users(self):

        # Get records that are syncing
        azure_ad_user_ids = self.env['azure.ad.user'].search([('azure_ad_sync_started', '=', True)])

        # If not azure users, return, prevents unnecessary code being executed
        if len(azure_ad_user_ids) == 0:
            return azure_ad_user_ids

        # Global rules, azure_ad_users following these don't need individual checking
        global_rules = self.env['res.partner.filter'].get_globally_followed_filters(self)

        to_sync = set()

        for user in azure_ad_user_ids:
            # Check if all syncing or following any global rule
            if (user.contact_sync_filter_options == 'all') or \
                    (not set(user.contact_sync_filters).isdisjoint(global_rules.ids)) or \
                    (user.contact_sync_filters.is_following_rules(partner=self, user=user)):
                try:
                    user_id = self.env['res.users'].search([('partner_id', '=', user.partner_id.id)])

                    self.sudo(user=user_id.id).env['res.partner'].check_access_rule('read')

                    to_sync.add(user.id)
                except:
                    pass

        return self.env['azure.ad.user'].browse(to_sync)
