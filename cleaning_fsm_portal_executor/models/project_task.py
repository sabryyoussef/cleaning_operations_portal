# -*- coding: utf-8 -*-
from odoo import _, api, fields, models
from odoo.exceptions import AccessError, ValidationError


class ProjectTask(models.Model):
    _inherit = 'project.task'

    fsm_portal_executor_id = fields.Many2one(
        'res.users',
        string='Portal cleaner',
        domain="[('share', '=', True), ('active', '=', True)]",
        index='btree_not_null',
        copy=False,
        help='Operational cleaner (portal user). Separate from internal assignees.',
    )
    fsm_portal_started = fields.Boolean(
        string='Visit started (portal)',
        default=False,
        copy=False,
        help='Set via portal when the cleaner starts the visit.',
    )
    fsm_portal_started_at = fields.Datetime(
        string='Started at (portal)',
        copy=False,
        help='Server time when the portal cleaner clicked Start Visit. Set once; not overwritten.',
    )
    fsm_portal_start_latitude = fields.Float(
        string='Start latitude (portal)',
        copy=False,
        digits=(16, 7),
        help='Browser geolocation at Start Visit when available; optional evidence only.',
    )
    fsm_portal_start_longitude = fields.Float(
        string='Start longitude (portal)',
        copy=False,
        digits=(16, 7),
        help='Browser geolocation at Start Visit when available; optional evidence only.',
    )
    fsm_portal_start_accuracy = fields.Float(
        string='Start GPS accuracy (m)',
        copy=False,
        digits=(16, 1),
        help='Reported accuracy in meters when the browser supplied it.',
    )
    fsm_portal_photo_before = fields.Image(
        string='Before photo (portal)',
        copy=False,
        help='Single before photo uploaded by the portal cleaner from the visit page.',
    )
    fsm_portal_photo_after = fields.Image(
        string='After photo (portal)',
        copy=False,
        help='Single after photo uploaded by the portal cleaner from the visit page.',
    )
    fsm_portal_photo_before_latitude = fields.Float(
        string='Before photo latitude (portal)',
        copy=False,
        digits=(16, 7),
        help='Optional browser geolocation when the before photo was uploaded.',
    )
    fsm_portal_photo_before_longitude = fields.Float(
        string='Before photo longitude (portal)',
        copy=False,
        digits=(16, 7),
    )
    fsm_portal_photo_before_accuracy = fields.Float(
        string='Before photo GPS accuracy (m)',
        copy=False,
        digits=(16, 1),
    )
    fsm_portal_photo_after_latitude = fields.Float(
        string='After photo latitude (portal)',
        copy=False,
        digits=(16, 7),
        help='Optional browser geolocation when the after photo was uploaded.',
    )
    fsm_portal_photo_after_longitude = fields.Float(
        string='After photo longitude (portal)',
        copy=False,
        digits=(16, 7),
    )
    fsm_portal_photo_after_accuracy = fields.Float(
        string='After photo GPS accuracy (m)',
        copy=False,
        digits=(16, 1),
    )
    fsm_portal_ended_at = fields.Datetime(
        string='Ended at (portal)',
        copy=False,
        help='Server time when the portal cleaner clicked End Visit. Set once; not overwritten.',
    )
    fsm_portal_visit_duration_text = fields.Char(
        string='Visit duration (portal)',
        compute='_compute_fsm_portal_visit_duration_text',
        help='Time between portal start and end timestamps (computed, not stored separately).',
    )
    fsm_portal_qr_entry_url = fields.Char(
        string='QR entry URL',
        compute='_compute_fsm_portal_qr_entry_url',
        help='Encode this URL in a QR code so the assigned portal cleaner can open the visit (after login).',
    )
    fsm_portal_late_start = fields.Boolean(
        string='Late check-in (vs planned start)',
        compute='_compute_fsm_portal_late_start',
        store=True,
        help='True when portal check-in time is after the task planned start (Field Service planning).',
    )
    fsm_portal_late_start_delay_text = fields.Char(
        string='Late by',
        compute='_compute_fsm_portal_late_start',
        store=True,
        help='Human-readable lateness when check-in is after the planned start.',
    )

    @api.depends('is_fsm', 'create_date', 'partner_id')
    def _compute_fsm_portal_qr_entry_url(self):
        base = self.env['ir.config_parameter'].sudo().get_param('web.base.url', '').rstrip('/')
        for task in self:
            if base and task.id and task.is_fsm:
                url = '%s/my/fsm-visit/%s' % (base, task.id)
                # Site id in query helps cleaners confirm the QR matches the scheduled site (Phase 2).
                if task.partner_id:
                    url += '?site=%s' % int(task.partner_id.id)
                task.fsm_portal_qr_entry_url = url
            else:
                task.fsm_portal_qr_entry_url = False

    @api.depends('is_fsm', 'planned_date_begin', 'fsm_portal_started_at')
    def _compute_fsm_portal_late_start(self):
        for task in self:
            task.fsm_portal_late_start = False
            task.fsm_portal_late_start_delay_text = False
            if (
                not task.is_fsm
                or not task.planned_date_begin
                or not task.fsm_portal_started_at
            ):
                continue
            if task.fsm_portal_started_at <= task.planned_date_begin:
                continue
            delta = task.fsm_portal_started_at - task.planned_date_begin
            secs = int(delta.total_seconds())
            if secs <= 0:
                continue
            task.fsm_portal_late_start = True
            task.fsm_portal_late_start_delay_text = self._format_fsm_portal_lateness_delay(secs)

    @staticmethod
    def _format_fsm_portal_lateness_delay(secs):
        """Return translated short text like '12 min late' (ceiling minutes, minimum 1)."""
        total_min = max(1, (secs + 59) // 60)
        h, m = divmod(total_min, 60)
        if h and m:
            return _('%dh %dmin late') % (h, m)
        if h:
            return _('%dh late') % h
        return _('%d min late') % total_min

    @api.depends('fsm_portal_started_at', 'fsm_portal_ended_at')
    def _compute_fsm_portal_visit_duration_text(self):
        for task in self:
            task.fsm_portal_visit_duration_text = False
            if not task.fsm_portal_started_at or not task.fsm_portal_ended_at:
                continue
            delta = task.fsm_portal_ended_at - task.fsm_portal_started_at
            secs = int(delta.total_seconds())
            if secs < 0:
                task.fsm_portal_visit_duration_text = _('Invalid (end before start)')
                continue
            h, rem = divmod(secs, 3600)
            m, s = divmod(rem, 60)
            parts = []
            if h:
                parts.append(_('%dh') % h)
            if m or h:
                parts.append(_('%dmin') % m)
            if not h and not m:
                parts.append(_('%ds') % s)
            task.fsm_portal_visit_duration_text = ' '.join(parts)

    @api.model
    def _portal_accessible_fields(self):
        """Allow portal users to read photo fields so /web/image can stream them (see project.task._has_field_access).

        Do not stack ``@tools.ormcache`` here: the parent already caches; a second layer can stay stale
        after upgrades and drop new fields from ``fields_get``, breaking the backend form (Owl: field undefined).
        """
        readable, writeable = super()._portal_accessible_fields()
        extra = frozenset({
            'fsm_portal_photo_before',
            'fsm_portal_photo_after',
            'fsm_portal_photo_before_latitude',
            'fsm_portal_photo_before_longitude',
            'fsm_portal_photo_before_accuracy',
            'fsm_portal_photo_after_latitude',
            'fsm_portal_photo_after_longitude',
            'fsm_portal_photo_after_accuracy',
            'fsm_portal_ended_at',
            'fsm_portal_visit_duration_text',
            'fsm_portal_start_latitude',
            'fsm_portal_start_longitude',
            'fsm_portal_start_accuracy',
            'fsm_portal_late_start',
            'fsm_portal_late_start_delay_text',
        })
        return readable | extra, writeable

    @api.constrains('fsm_portal_executor_id')
    def _check_fsm_portal_executor_id(self):
        for task in self:
            user = task.fsm_portal_executor_id
            if not user:
                continue
            if not user.active:
                raise ValidationError(_('The portal cleaner must be active.'))
            if not user.share:
                raise ValidationError(_('The portal cleaner must be a portal-type user (not an internal user).'))
            if not user.has_group('base.group_portal'):
                raise ValidationError(_('The portal cleaner must belong to the Portal group.'))

    def write(self, vals):
        # Broad guard: block any portal ORM write on tasks (controller mutates via sudo after checks).
        # May be tightened later (e.g. allow-list of field keys for portal) if needed.
        if not self.env.su and self.env.user.has_group('base.group_portal'):
            raise AccessError(_('Portal users cannot edit tasks from the backend.'))
        return super().write(vals)
