# -*- coding: utf-8 -*-


{
    'name': 'Bambora Payment Acquirer',
    'category': 'Payment Gateway',
    'summary': 'Payment Acquirer: Bambora Implementation',
    'version': '1.0',
	'website': 'http://www.vkdata.dk',
    'author': 'vkdata',
    'description': """Bambora (ePay) Acquirer""",
    'depends': ['payment'],
    'data': [
        'views/bambora.xml',
        'views/payment_acquirer.xml',
        'data/bambora.xml',
    ],
    'images': [
        'static/description/bambora_payment_gateway_banner.png',
    ],
	
	'license': 'Other proprietary',
}
