{
    'name': "Website Custom Footer",
    'version': "1.0",
    'author': "VK Data",
    'category': "Web",
    'summary': "Custom footer for multi website",
    'description': "This module allows you to add a custom footer from the backend",
    'license':'LGPL-3',
	'website': 'http://www.vkdata.dk/',
    'data': [      
		'views/template.xml',
        'views/assets.xml',
        'views/config_views.xml',
    ],
    'demo': [],
    'images':[
        'static/description/icon.png',
    ],
	'price': 0.00,
	'currency': 'USD',
    'depends': ['website','website_mass_mailing'],
    'installable': True,
}
