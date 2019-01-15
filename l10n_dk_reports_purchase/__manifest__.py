{
    'name': 'Denmark - Localized Purchase Reports',
    'version': '1.0',
    'category': 'Localization/Reports',
    'description': """
        Localized reports for Purchase in Denmark
    """,
    'author': 'VK Data ApS',
    'website': 'http://www.vkdata.dk',
    'depends': [
        'purchase',
        'l10n_dk',
        'l10n_dk_reports'
    ],
    'data': [
        'views/l10n_dk_report_purchaseorder.xml',
    ],
    'installable': True,
    'auto_install': True,
    'license': 'LGPL-3',
}