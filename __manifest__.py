# -*- coding: utf-8 -*-
# Copyright 2016 Vauxoo - https://www.vauxoo.com/
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "Umnico",
    "version": "15.0.1.0.0",
    "author": "based on Vauxoo, Odoo Community Association (OCA)",
    "category": "Integration",
    "website": "https://www.vauxoo.com",
    "license": "AGPL-3",
    "depends": [
        "web",
    ],
    "external_dependencies": {
        "python": [
            "ipaddress",
            "requests",
        ],
    },
    "data": [
        "security/ir.model.access.csv",
        "views/webhook_views.xml",
        "data/webhook.xml",
    ],
    "demo": [
        "demo/webhook_demo.xml",
    ],
    "installable": True,
    "auto_install": False,
}
