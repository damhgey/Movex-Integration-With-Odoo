# -*- coding: utf-8 -*-
{
    'name': "Base Delivery Integration",

    'summary': """Base Delivery Integration for shipment providers like Aramex and Movex, etc..""",

    'description': """
        Base Delivery Integration to put the base workflow of the shipment integration
        to build on it a integration with shipment provider like Aramex and Movex, etc..
     """,

    'author': "Ahmed Elsayed Aldamhogy",
    'category': 'Warehouse',
    'version': '13.0.1',

    'depends': ['base', 'stock', 'sale'],

    'data': [
        'security/security.xml',
        'views/stock_picking.xml'
    ],
}
