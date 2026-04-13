# -*- coding: utf-8 -*-
import base64
from urllib.parse import quote

from odoo import fields, http
from odoo.exceptions import UserError, ValidationError
from odoo.http import request

_ALLOWED_IMAGE_TYPES = frozenset({'image/jpeg', 'image/png', 'image/webp', 'image/gif'})
_MAX_IMAGE_BYTES = 15 * 1024 * 1024


def _fsm_parse_optional_float(raw):
    if raw is None:
        return None
    s = (raw if isinstance(raw, str) else str(raw)).strip()
    if not s:
        return None
    try:
        return float(s)
    except ValueError:
        return None


def _fsm_portal_geo_from_request(form):
    """Return (vals_dict, gps_flag) where gps_flag is 'ok' or 'miss'. Never raises."""
    return _fsm_portal_geo_from_request_keys(
        form,
        'fsm_portal_start_geo_lat',
        'fsm_portal_start_geo_lon',
        'fsm_portal_start_geo_accuracy',
        {
            'lat': 'fsm_portal_start_latitude',
            'lon': 'fsm_portal_start_longitude',
            'acc': 'fsm_portal_start_accuracy',
        },
    )


def _fsm_portal_geo_from_request_keys(form, lat_key, lon_key, acc_key, field_map):
    """Map browser geo POST keys to task float fields. Returns (vals_dict, 'ok'|'miss')."""
    lat = _fsm_parse_optional_float(form.get(lat_key))
    lon = _fsm_parse_optional_float(form.get(lon_key))
    acc = _fsm_parse_optional_float(form.get(acc_key))
    vals = {}
    if lat is None or lon is None:
        return vals, 'miss'
    if not (-90.0 <= lat <= 90.0 and -180.0 <= lon <= 180.0):
        return vals, 'miss'
    vals[field_map['lat']] = lat
    vals[field_map['lon']] = lon
    if acc is not None and acc >= 0.0 and 'acc' in field_map:
        vals[field_map['acc']] = acc
    return vals, 'ok'


class CleaningFsmPortal(http.Controller):
    """Strictly controlled portal routes; only sudo write after authorization.

    Portal users may lack field-level read access on ``fsm_portal_executor_id`` when
    searching in a normal user env. List/detail therefore use a narrow ``sudo()``
    search/browse scoped by ``(fsm_portal_executor_id = uid)`` and ``is_fsm`` — same
    authorization intent as the ir.rule, without exposing other users' tasks.
    """

    def _ensure_portal_user(self):
        """Return a werkzeug Response to short-circuit, or None if the user may continue."""
        user = request.env.user
        if user._is_public():
            return request.redirect('/web/login?redirect=%s' % request.httprequest.path)
        if not user.has_group('base.group_portal'):
            return request.redirect('/my')
        return None

    def _portal_fsm_domain(self, user):
        return [
            ('fsm_portal_executor_id', '=', user.id),
            ('is_fsm', '=', True),
        ]

    def _task_for_portal_executor(self, task_id, user):
        """Return the task in sudo env if it belongs to this portal executor; else empty."""
        task = request.env['project.task'].sudo().browse(int(task_id)).exists()
        if not task:
            return task
        if task.fsm_portal_executor_id != user or not task.is_fsm:
            return request.env['project.task']
        return task

    @http.route(
        ['/my/fsm-visit/<int:task_id>'],
        type='http',
        auth='public',
        website=True,
        readonly=True,
    )
    def portal_fsm_qr_entry(self, task_id, **kwargs):
        """Short URL for QR codes → login if needed, then same visit flow as /my/fsm-visits/<id>."""
        site = request.params.get('site')
        path = '/my/fsm-visits/%s' % int(task_id)
        if site:
            path = '%s?site=%s' % (path, quote(str(site), safe=''))
        if request.env.user._is_public():
            return request.redirect('/web/login?redirect=%s' % quote(path, safe=''))
        return request.redirect(path)

    @http.route(['/my/fsm-visits'], type='http', auth='user', website=True)
    def portal_fsm_visit_list(self, **kwargs):
        redir = self._ensure_portal_user()
        if redir is not None:
            return redir
        user = request.env.user
        domain = self._portal_fsm_domain(user)
        tasks = request.env['project.task'].sudo().search(domain, order='id desc')
        values = {
            'tasks': tasks,
            'page_name': 'fsm_visits',
        }
        return request.render('cleaning_fsm_portal_executor.portal_fsm_visit_list', values)

    @http.route(['/my/fsm-visits/<int:task_id>'], type='http', auth='user', website=True)
    def portal_fsm_visit_detail(self, task_id, access_token=None, **kwargs):
        redir = self._ensure_portal_user()
        if redir is not None:
            return redir
        user = request.env.user
        task_sudo = request.env['project.task'].sudo().browse(int(task_id))
        if not task_sudo.exists():
            return request.render('cleaning_fsm_portal_executor.portal_fsm_visit_missing', {'task_id': task_id})
        task = self._task_for_portal_executor(task_id, user)
        if not task:
            return request.render('cleaning_fsm_portal_executor.portal_fsm_visit_denied', {})
        site_param = request.params.get('site')
        site_mismatch = False
        if site_param:
            try:
                spid = int(site_param)
            except (TypeError, ValueError):
                site_mismatch = True
            else:
                if not task.partner_id or task.partner_id.id != spid:
                    site_mismatch = True
        values = {
            'task': task,
            'page_name': 'fsm_visit_detail',
            'fsm_portal_site_qr_mismatch': site_mismatch,
        }
        return request.render('cleaning_fsm_portal_executor.portal_fsm_visit_detail', values)

    @http.route(
        ['/my/fsm-visits/<int:task_id>/start'],
        type='http',
        auth='user',
        methods=['POST'],
        website=True,
        csrf=True,
    )
    def portal_fsm_visit_start(self, task_id, **kwargs):
        redir = self._ensure_portal_user()
        if redir is not None:
            return redir
        user = request.env.user
        task = self._task_for_portal_executor(task_id, user)
        if not task:
            return request.not_found()
        if task.fsm_portal_started:
            return request.redirect('/my/fsm-visits/%s' % task.id)
        vals = {'fsm_portal_started': True}
        # Evidence timestamp: set once on first start only (never overwrite — audit-safe).
        if not task.fsm_portal_started_at:
            vals['fsm_portal_started_at'] = fields.Datetime.now()
        geo_vals, gps_flag = _fsm_portal_geo_from_request(request.httprequest.form)
        # GPS is optional evidence only: merge when valid; start always proceeds.
        vals.update(geo_vals)
        task.sudo().write(vals)
        return request.redirect('/my/fsm-visits/%s?started=1&gps=%s' % (task.id, gps_flag))

    @http.route(
        ['/my/fsm-visits/<int:task_id>/end'],
        type='http',
        auth='user',
        methods=['POST'],
        website=True,
        csrf=True,
    )
    def portal_fsm_visit_end(self, task_id, **kwargs):
        redir = self._ensure_portal_user()
        if redir is not None:
            return redir
        user = request.env.user
        task = self._task_for_portal_executor(task_id, user)
        if not task:
            return request.not_found()
        if task.fsm_portal_ended_at:
            return request.redirect('/my/fsm-visits/%s' % task.id)
        # Require both flag and check-in timestamp (consistent start evidence, not boolean alone).
        if not task.fsm_portal_started or not task.fsm_portal_started_at:
            return request.redirect('/my/fsm-visits/%s?end_err=not_started' % task.id)
        vals = {'fsm_portal_ended_at': fields.Datetime.now()}
        geo_vals, gps_flag = _fsm_portal_geo_from_request_keys(
            request.httprequest.form,
            'fsm_portal_end_geo_lat',
            'fsm_portal_end_geo_lon',
            'fsm_portal_end_geo_accuracy',
            {
                'lat': 'fsm_portal_end_latitude',
                'lon': 'fsm_portal_end_longitude',
                'acc': 'fsm_portal_end_accuracy',
            },
        )
        vals.update(geo_vals)
        task.sudo().write(vals)
        return request.redirect('/my/fsm-visits/%s?ended=1&gps=%s' % (task.id, gps_flag))

    def _portal_fsm_upload_image(self, task, upload, field_name):
        """Return None on success, or short error code string."""
        if not upload or not upload.filename:
            return 'missing'
        ctype = (upload.content_type or '').split(';')[0].strip().lower()
        if ctype not in _ALLOWED_IMAGE_TYPES:
            return 'type'
        raw = upload.read()
        if len(raw) > _MAX_IMAGE_BYTES:
            return 'size'
        try:
            task.sudo().write({field_name: base64.b64encode(raw)})
        except (UserError, ValidationError):
            return 'invalid'
        return None

    @http.route(
        ['/my/fsm-visits/<int:task_id>/photo/before'],
        type='http',
        auth='user',
        methods=['POST'],
        website=True,
        csrf=True,
    )
    def portal_fsm_photo_before(self, task_id, **kwargs):
        redir = self._ensure_portal_user()
        if redir is not None:
            return redir
        user = request.env.user
        task = self._task_for_portal_executor(task_id, user)
        if not task:
            return request.not_found()
        if task.fsm_portal_ended_at:
            return request.redirect('/my/fsm-visits/%s' % task.id)
        if task.fsm_portal_photo_before:
            return request.redirect('/my/fsm-visits/%s?photo_err=locked_before' % task.id)
        err = self._portal_fsm_upload_image(
            task, request.httprequest.files.get('photo'), 'fsm_portal_photo_before'
        )
        if err:
            return request.redirect('/my/fsm-visits/%s?photo_err=%s' % (task.id, err))
        geo_vals, _gps = _fsm_portal_geo_from_request_keys(
            request.httprequest.form,
            'fsm_portal_photo_before_geo_lat',
            'fsm_portal_photo_before_geo_lon',
            'fsm_portal_photo_before_geo_accuracy',
            {
                'lat': 'fsm_portal_photo_before_latitude',
                'lon': 'fsm_portal_photo_before_longitude',
                'acc': 'fsm_portal_photo_before_accuracy',
            },
        )
        if geo_vals:
            task.sudo().write(geo_vals)
        return request.redirect('/my/fsm-visits/%s?photo_ok=before' % task.id)

    @http.route(
        ['/my/fsm-visits/<int:task_id>/photo/after'],
        type='http',
        auth='user',
        methods=['POST'],
        website=True,
        csrf=True,
    )
    def portal_fsm_photo_after(self, task_id, **kwargs):
        redir = self._ensure_portal_user()
        if redir is not None:
            return redir
        user = request.env.user
        task = self._task_for_portal_executor(task_id, user)
        if not task:
            return request.not_found()
        if task.fsm_portal_ended_at:
            return request.redirect('/my/fsm-visits/%s' % task.id)
        if task.fsm_portal_photo_after:
            return request.redirect('/my/fsm-visits/%s?photo_err=locked_after' % task.id)
        err = self._portal_fsm_upload_image(
            task, request.httprequest.files.get('photo'), 'fsm_portal_photo_after'
        )
        if err:
            return request.redirect('/my/fsm-visits/%s?photo_err=%s' % (task.id, err))
        geo_vals, _gps = _fsm_portal_geo_from_request_keys(
            request.httprequest.form,
            'fsm_portal_photo_after_geo_lat',
            'fsm_portal_photo_after_geo_lon',
            'fsm_portal_photo_after_geo_accuracy',
            {
                'lat': 'fsm_portal_photo_after_latitude',
                'lon': 'fsm_portal_photo_after_longitude',
                'acc': 'fsm_portal_photo_after_accuracy',
            },
        )
        if geo_vals:
            task.sudo().write(geo_vals)
        return request.redirect('/my/fsm-visits/%s?photo_ok=after' % task.id)
