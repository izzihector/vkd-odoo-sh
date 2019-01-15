{
    'name': "Website Facebook Pixel",
    'version': "1.0",
    'author': "VK Data",
    'category': "Web",
    'summary': "Add facebook Tracking pixel to your Odoo website",
    'description': "This module allows you to add facebook Tracking code and tracking pixel to your Odoo website",
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
