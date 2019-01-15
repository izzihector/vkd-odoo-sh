from odoo import models, fields, api, _
import requests
import json
import logging

_logger = logging.getLogger(__name__)

class PartnerLine(models.TransientModel):
    _name = 'partner.line'

    name = fields.Char()
    street = fields.Char()
    street2 = fields.Char()
    zip = fields.Char()
    email = fields.Char()
    city = fields.Char()
    phone = fields.Char()
    fax = fields.Char()
    vat = fields.Char(string="TIN")
    partner = fields.Many2one('res.partner')
    ad_protected = fields.Boolean(string="Ad Protected", help="It is illegal to send unsolicited ads to this partner")

    def confirm_selection(self):
        partner_id = self.env['res.partner'].search([('id', '=', self.partner.id)])
        vals = {}
        vals['id'] = partner_id.id
        vals['name'] = self.name
        vals['street'] = self.street
        vals['street2'] = self.street2
        vals['zip'] = self.zip
        vals['email'] = self.email
        vals['city'] = self.city
        vals['phone'] = self.phone
        vals['fax'] = self.fax
        vals['vat'] = self.vat
        vals['is_company'] = True
        vals['ad_protected'] = self.ad_protected

        denmark = self.env['res.country'].search([('code', '=', 'DK')])
        vals['country_id'] = denmark.id
        partner_id.write(vals)

        # TODO Find a better way to reload the form window
        return {'type': 'ir.actions.client', 'tag': 'reload'}

class ResPartner(models.Model):
    _inherit = 'res.partner'

    search_field = fields.Char(string="Search field", help="Enter the CVR-number or the name of the contact you want to create. This will search the CVR database, and automatically fill the relevant fields.")
    virk_user = fields.Char(string="Virk.dk Username", related="company_id.virk_user")
    virk_pass = fields.Char(string="Virk.dk Password", related="company_id.virk_pass")
    ad_protected = fields.Boolean(string="Ad Protected", help="It is illegal to send unsolicited ads to this partner")
    search_results = fields.One2many('partner.line', 'partner')
    name = fields.Char(index=True, default="Navn")

    @api.multi
    def search_virk_dk(self):

        # Delete previous results
        self.env['partner.line'].search([]).unlink()

        # TODO Return errors as a popup message for the user
        if not self.search_field:
            return
        if not self.virk_user:
            self.search_field = 'Virk.dk Username is missing'
            return
        if not self.virk_pass:
            self.search_field = 'Virk.dk Password is missing'
            return

        headers = {"Content-type": "application/json;charset=utf-8"}

        # Virk.dk query
        if self.search_field.isdigit() and len(self.search_field) is 8:
            query = json.dumps({"from": 0, "size": 1, "_source": ["Vrvirksomhed.cvrNummer", "Vrvirksomhed.virksomhedMetadata.nyesteNavn.navn", "Vrvirksomhed.virksomhedMetadata.nyesteBeliggenhedsadresse", "Vrvirksomhed.telefonNummer", "Vrvirksomhed.telefaxNummer", "Vrvirksomhed.elektroniskPost", "Vrvirksomhed.reklamebeskyttet"],
            "query": {"term": {"Vrvirksomhed.cvrNummer": self.search_field}}})
        else:
            query = json.dumps({"from": 0, "size": 10, "_source": ["Vrvirksomhed.cvrNummer", "Vrvirksomhed.virksomhedMetadata.nyesteNavn.navn", "Vrvirksomhed.virksomhedMetadata.nyesteBeliggenhedsadresse", "Vrvirksomhed.telefonNummer", "Vrvirksomhed.telefaxNummer", "Vrvirksomhed.elektroniskPost", "Vrvirksomhed.reklamebeskyttet"],
            "query": {"query_string": {"default_field": "Vrvirksomhed.virksomhedMetadata.nyesteNavn.navn", "query": self.search_field}}})

        response = requests.post('http://distribution.virk.dk/cvr-permanent/_search', auth=(self.virk_user, self.virk_pass), data=query, headers=headers)

        if not response:
            _logger.info(' No response from Virk.dk ')
            self.search_field = 'No response from Virk.dk'
            return

        result = json.loads(response.text)

        if not result['hits']['hits']:
            _logger.info(' No company found ')
            self.search_field = 'No company found'
            return

        doc = result['hits']['hits']

        # Partner line creation
        for r in doc:
            vals = {}
            if r['_source']['Vrvirksomhed']['virksomhedMetadata']['nyesteNavn']['navn']:
                vals['name'] = r['_source']['Vrvirksomhed']['virksomhedMetadata']['nyesteNavn']['navn']
            if r['_source']['Vrvirksomhed']['virksomhedMetadata']['nyesteBeliggenhedsadresse']:
                vals['zip'] = str(r['_source']['Vrvirksomhed']['virksomhedMetadata']['nyesteBeliggenhedsadresse']['postnummer'])
                vals['street'] = r['_source']['Vrvirksomhed']['virksomhedMetadata']['nyesteBeliggenhedsadresse']['vejnavn'] + " " + str(r['_source']['Vrvirksomhed']['virksomhedMetadata']['nyesteBeliggenhedsadresse']['husnummerFra'])
                vals['street2'] = r['_source']['Vrvirksomhed']['virksomhedMetadata']['nyesteBeliggenhedsadresse']['bynavn']
                vals['city'] = r['_source']['Vrvirksomhed']['virksomhedMetadata']['nyesteBeliggenhedsadresse']['postdistrikt']
            if r['_source']['Vrvirksomhed']['telefonNummer']:
                vals['phone'] = r['_source']['Vrvirksomhed']['telefonNummer'][-1]['kontaktoplysning']
            if r['_source']['Vrvirksomhed']['telefaxNummer']:
                vals['fax'] = r['_source']['Vrvirksomhed']['telefaxNummer'][-1]['kontaktoplysning']
            if r['_source']['Vrvirksomhed']['elektroniskPost']:
                vals['email'] = r['_source']['Vrvirksomhed']['elektroniskPost'][-1]['kontaktoplysning']
            vals['vat'] = "DK" + str(r['_source']['Vrvirksomhed']['cvrNummer'])
            vals['partner'] = self.id
            if r['_source']['Vrvirksomhed']['reklamebeskyttet']:
                vals['ad_protected'] = True
            self.search_results.create(vals)
