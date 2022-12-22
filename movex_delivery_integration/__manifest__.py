# -*- coding: utf-8 -*-
{
    'name': "Movex Delivery Integration",

    'summary': """ Send your shipments from pickings to Movex and track them from Odoo""",

    'description': """
        Send multi Movex shipments form picking in odoo with auto fill information of the shipments
        with pickings info and get AWB number,tracking link and Label PDF link after send shipments
        and store them in fields in pickings and shipments state updated from Movex to Odoo automatically.
    """,

    'author': "Ahmed Elsayed Aldamhogy",

    'category': 'Warehouse',

    'version': '13.0.1',

    'depends': ['stock', 'delivery', 'mail', 'base_delivery_integration'],

    'data': [
        'security/ir.model.access.csv',
        'wizard/send_movex_shipment_information_wizard.xml',
        'data/data.xml',
        'data/scheduled_action.xml',
        'views/delivery_movex_view.xml',
        'views/stock_picking_view.xml',
    ],
}
