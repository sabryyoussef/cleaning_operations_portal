# -*- coding: utf-8 -*-
"""Remove legacy ``fsm_portal_qr_image_url`` nodes from stored view arch (Owl: field undefined)."""

import logging

from lxml import etree

from odoo import SUPERUSER_ID, api

_logger = logging.getLogger(__name__)

_XPATHS = (
    ".//*[local-name()='field'][@name='fsm_portal_qr_image_url']",
    ".//*[local-name()='label'][@for='fsm_portal_qr_image_url']",
)


def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    views = env['ir.ui.view'].sudo().search([('arch_db', 'ilike', 'fsm_portal_qr_image_url')])
    for view in views:
        arch = view.arch_db or ''
        if 'fsm_portal_qr_image_url' not in arch:
            continue
        try:
            root = etree.fromstring(arch.encode('utf-8'))
        except etree.XMLSyntaxError:
            _logger.warning(
                'Skipping ir.ui.view id=%s: invalid XML while stripping fsm_portal_qr_image_url',
                view.id,
            )
            continue
        changed = False
        for xp in _XPATHS:
            for node in root.xpath(xp):
                parent = node.getparent()
                if parent is not None:
                    parent.remove(node)
                    changed = True
        if not changed:
            continue
        new_arch = etree.tostring(root, encoding='unicode')
        view.write({'arch_db': new_arch})
        _logger.info(
            'Removed legacy fsm_portal_qr_image_url from ir.ui.view id=%s (%s)',
            view.id,
            view.name or '',
        )
