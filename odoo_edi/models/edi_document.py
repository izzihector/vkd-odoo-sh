# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
import logging, json, requests
_logger = logging.getLogger(__name__)

API_ROOT = "https://api.b2bbackbone.com/api"

class EdiDocument(models.TransientModel):
    _name = 'odoo_edi.document'
    _description = 'Odoo EDI Document'

    def send_document(self, document, document_id):
        self.validate_settings()
        server_address = API_ROOT + "/document/upload"
        settings = self.env.user.company_id
        token = settings.odoo_edi_token
        if not self.env.user.company_id.edi_mode == 'development':
            headers = {
                'Content-Type': 'application/json; charset=utf8',
                'Authorization': 'Bearer {0}'.format(token)
            }
            result = requests.post(server_address, headers=headers, json=document)
            if not result.status_code == 200:
                _logger.info('Error during request:')
                _logger.info(result)
            _logger.info(result.status_code)
            _logger.info(result.text)
        else:
            # print(document)
            f = open('/tmp/' + document_id + '.json', 'w')
            f.write(json.dumps(document, ensure_ascii=False))
            f.close()
            _logger.info('odoo_edi is running in DEVELOPMENT mode and therefore nothing has been submitted to the servers. You can find your file in the /tmp directory')

    def recieve_document(self):
        raise UserError(_("The odoo_edi.document.recieve_document method is not implemented for this document type"))

    def create_edi(self, document):
        raise UserError(_("The odoo_edi.document.create_edi method is not implemented for this document type"))

    def validate_settings(self):
        if not self.env.user.company_id.company_registry:
            raise UserError(_('The current company, %s, does not have a company registration number or GLN identification/number, which is required for EDI invoicing') % self.env.user.company_id.name)
        if self.env.user.company_id.odoo_edi_token == "" or not self.env.user.company_id.odoo_edi_token:
            raise UserError(_('Please define the FlexEDI username and FlexEDI password before sending an invoice'))
        if not self.env.user.company_id.bank_journal_id:
            raise UserError(_('The current company, %s, does not have a default bank journal configured, which is required for EDI invoicing') % self.env.user.company_id.name)

