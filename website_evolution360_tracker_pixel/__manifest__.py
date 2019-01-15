{
    'name': "Evolution360 tracker pixel",
    'version': "1.0",
    'author': "VK Data",
    'category': "Web",
	'sequence': 390,
    'summary': "Add Evolution360 tracker pixel to your Odoo website",
    'description': "",
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
	'price': 0.00,
	'currency': 'USD',
    'depends': ['website'],
    'installable': True,
}
