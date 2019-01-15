{
    'name': "Website Lead Forensics Tracking",
    'version': "1.0",
    'author': "VK Data",
    'category': "Web",
    'summary': "Add Lead Forensics traking code to your Odoo website",
    'description': "This module allows you add traking code from Lead Forensics to your website",
    'license':'LGPL-3',
	'website': 'http://www.vkdata.dk/',
    'data': [
		'views/form.xml',        
		'views/template.xml',
    ],
    'demo': [],
    'images':[
        'static/description/icon.png',
    ],
	'price': 50.00,
	'currency': 'USD',
    'depends': ['website'],
    'installable': True,
}
