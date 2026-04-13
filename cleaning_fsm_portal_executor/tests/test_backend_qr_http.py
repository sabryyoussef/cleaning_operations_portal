# -*- coding: utf-8 -*-
import importlib.util

from odoo.tests import HttpCase, tagged

HAS_QRCODE = importlib.util.find_spec('qrcode') is not None


@tagged('post_install', '-at_install', 'cleaning_fsm_portal')
class TestBackendQrHttp(HttpCase):
    """PNG route ``/cleaning_fsm_portal/fsm_qr_png/<task>`` (auth user, project user).

    Uses ``admin`` + ``authenticate`` so ``check_session`` matches; prefers an
    FSM task already stored in the DB so the HTTP request sees the row.
    """

    def setUp(self):
        super().setUp()
        admin = self.env.ref('base.user_admin')
        if not admin.has_group('project.group_project_user'):
            admin.sudo().write({'group_ids': [(4, self.env.ref('project.group_project_user').id)]})
        self.task = self.env['project.task'].search(
            [('project_id.is_fsm', '=', True), ('partner_id', '!=', False)],
            limit=1,
            order='id desc',
        )
        if not self.task:
            partner = self.env['res.partner'].create({'name': 'QR Site'})
            fsm_project = self.env['project.project'].create({
                'name': 'QR FSM Project',
                'is_fsm': True,
                'company_id': self.env.company.id,
            })
            self.task = self.env['project.task'].create({
                'name': 'QR Task',
                'project_id': fsm_project.id,
                'partner_id': partner.id,
            })
        self.assertTrue(self.task.fsm_portal_qr_entry_url)

    def test_qr_png_requires_auth_or_redirect(self):
        res = self.url_open(f'/cleaning_fsm_portal/fsm_qr_png/{self.task.id}', allow_redirects=False)
        self.assertIn(res.status_code, (301, 302, 303, 401, 403, 404))

    def test_qr_png_authenticated_returns_png_when_qrcode_installed(self):
        if not HAS_QRCODE:
            self.skipTest('Python qrcode package not installed')
        self.authenticate('admin', 'admin')
        res = self.url_open(f'/cleaning_fsm_portal/fsm_qr_png/{self.task.id}')
        self.assertEqual(res.status_code, 200)
        ctype = (res.headers.get('Content-Type') or '').split(';')[0].strip()
        self.assertEqual(ctype, 'image/png')

    def test_qr_png_unknown_task_404(self):
        if not HAS_QRCODE:
            self.skipTest('Python qrcode package not installed')
        self.authenticate('admin', 'admin')
        # Avoid colliding with an existing row id in a populated demo DB.
        max_id = max(self.env['project.task'].search([], order='id desc', limit=1).ids + [0])
        res = self.url_open('/cleaning_fsm_portal/fsm_qr_png/%s' % (max_id + 10**9,))
        self.assertEqual(res.status_code, 404)
