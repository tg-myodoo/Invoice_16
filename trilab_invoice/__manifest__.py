# noinspection PyStatementEffect
{
    'name': 'Trilab Invoice PL',
    'author': 'Trilab',
    'website': "https://trilab.pl",
    'version': '2.107',
    'category': 'Accounting',
    'summary': 'Base module to manage invoice in PL',
    'description': '''Base module to manage invoices and invoice correction
    according to Polish law and best practices''',
    'depends': [
        'web',
        'account',
        'sale',
        'sale_management',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/account_move.xml',
        'views/account_move_reversal.xml',
        'views/account_move_views.xml',
        'views/sale_advance_payment_inv.xml',
        'views/sale_views.xml',
        'views/res_currency_views.xml',
        'views/res_config_settings_views.xml',
        'views/report_templates.xml',
        # 15->16: duplicate
        'views/report_duplicate.xml',
    ],
    'images': [
        'static/description/banner.png',
        'static/description/invoice.png',
    ],
    # 15->16: restoring odoo-like styles in documents
    # 'assets': {
    #     'web.report_assets_common': [
    #         'trilab_invoice/static/src/scss/layout_boxed.scss',
    #     ],
    # },
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'OPL-1',
    'price': 140.0,
    'currency': 'EUR'
}
