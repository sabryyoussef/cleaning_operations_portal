# -*- coding: utf-8 -*-
"""Backend-only QR PNG (no Binary field on the form — avoids Owl / fields_get edge cases)."""
import io

from odoo import http
from odoo.exceptions import AccessError
from odoo.http import request


class CleaningFsmBackendQr(http.Controller):
    @http.route(
        ['/cleaning_fsm_portal/fsm_qr_png/<int:task_id>'],
        type='http',
        auth='user',
        readonly=True,
    )
    def fsm_portal_qr_png(self, task_id, **kwargs):
        """PNG for the portal QR entry URL. Requires task read + project user."""
        task = request.env['project.task'].browse(int(task_id)).exists()
        if not task or not task.is_fsm:
            return request.not_found()
        if not request.env.user.has_group('project.group_project_user'):
            return request.not_found()
        try:
            task.check_access('read')
        except AccessError:
            return request.not_found()
        url = task.fsm_portal_qr_entry_url
        if not url:
            return request.not_found()
        try:
            import qrcode  # noqa: PLC0415
        except ImportError:
            return request.not_found()
        buf = io.BytesIO()
        qrcode.make(url).save(buf, format='PNG')
        return request.make_response(
            buf.getvalue(),
            headers=[
                ('Content-Type', 'image/png'),
                ('Cache-Control', 'private, max-age=300'),
            ],
        )
