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
    fsm_cleaning_site_id = fields.Many2one(
        'cleaning.site',
        string='Cleaning site',
        copy=False,
        help='Dedicated site record for this visit (demo-level operational master data).',
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
    fsm_portal_end_latitude = fields.Float(
        string='End latitude (portal)',
        copy=False,
        digits=(16, 7),
        help='Browser geolocation at End Visit when available; optional evidence only.',
    )
    fsm_portal_end_longitude = fields.Float(
        string='End longitude (portal)',
        copy=False,
        digits=(16, 7),
    )
    fsm_portal_end_accuracy = fields.Float(
        string='End GPS accuracy (m)',
        copy=False,
        digits=(16, 1),
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
    fsm_portal_late_notice_posted = fields.Boolean(
        string='Late check-in chatter notice posted',
        default=False,
        copy=False,
        help='Internal: a one-time chatter note was posted when check-in was late (manager-facing alert).',
    )

    @api.depends('is_fsm', 'create_date', 'partner_id', 'fsm_cleaning_site_id')
    def _compute_fsm_portal_qr_entry_url(self):
        base = self.env['ir.config_parameter'].sudo().get_param('web.base.url', '').rstrip('/')
        for task in self:
            if base and task.id and task.is_fsm:
                url = '%s/my/fsm-visit/%s' % (base, task.id)
                params = []
                # Keep legacy partner-based site hint and add dedicated site id when available.
                if task.fsm_cleaning_site_id:
                    params.append('site_id=%s' % int(task.fsm_cleaning_site_id.id))
                if task.partner_id:
                    params.append('site=%s' % int(task.partner_id.id))
                if params:
                    url += '?%s' % '&'.join(params)
                task.fsm_portal_qr_entry_url = url
            else:
                task.fsm_portal_qr_entry_url = False

    @api.onchange('fsm_cleaning_site_id')
    def _onchange_fsm_cleaning_site_id(self):
        for task in self:
            site = task.fsm_cleaning_site_id
            if site and site.partner_id and not task.partner_id:
                task.partner_id = site.partner_id

    @api.constrains('fsm_cleaning_site_id', 'partner_id')
    def _check_fsm_cleaning_site_partner(self):
        for task in self:
            site = task.fsm_cleaning_site_id
            if not site or not site.partner_id or not task.partner_id:
                continue
            if site.partner_id != task.partner_id:
                raise ValidationError(
                    _('The selected cleaning site customer must match the task customer/site contact.')
                )

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
            task.fsm_portal_late_start_delay_text = task._format_fsm_portal_lateness_delay(secs)

    def _format_fsm_portal_lateness_delay(self, secs):
        """Return translated short text like '12 min late' (ceiling minutes, minimum 1)."""
        _ = self.env._
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
            _ = task.env._
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
            'fsm_portal_end_latitude',
            'fsm_portal_end_longitude',
            'fsm_portal_end_accuracy',
            'fsm_portal_late_start',
            'fsm_portal_late_start_delay_text',
        })
        return readable | extra, writeable

    @api.model_create_multi
    def create(self, vals_list):
        tasks = super().create(vals_list)
        if not self.env.context.get('fsm_portal_skip_late_notice'):
            tasks.flush_recordset(
                ['fsm_portal_late_start', 'fsm_portal_late_start_delay_text', 'fsm_portal_late_notice_posted']
            )
            tasks._fsm_portal_post_late_checkin_notice()
        return tasks

    def _fsm_portal_post_late_checkin_notice(self):
        """Post a single internal chatter note when a visit becomes late (brief-friendly alert)."""
        odoobot = self.env.ref('base.partner_root', raise_if_not_found=False)
        author_id = odoobot.id if odoobot else self.env.user.partner_id.id
        for task in self.filtered(lambda t: t.is_fsm and t.fsm_portal_late_start and not t.fsm_portal_late_notice_posted):
            delay = task.fsm_portal_late_start_delay_text or task.env._('(delay unknown)')
            body = task.env._('Late check-in alert: portal start is after the planned start (%s).') % delay
            task.sudo().message_post(
                body=body,
                message_type='notification',
                subtype_xmlid='mail.mt_note',
                author_id=author_id,
            )
            task.with_context(fsm_portal_skip_late_notice=True).sudo().write({'fsm_portal_late_notice_posted': True})

    def action_fsm_open_qr_png(self):
        """Open PNG QR for this task in a new tab."""
        self.ensure_one()
        if not self.is_fsm or not self.id:
            return False
        return {
            'type': 'ir.actions.act_url',
            'url': '/cleaning_fsm_portal/fsm_qr_png/%s' % int(self.id),
            'target': 'new',
        }

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
        if self.env.context.get('fsm_portal_skip_late_notice'):
            return super().write(vals)
        res = super().write(vals)
        self._fsm_portal_post_late_checkin_notice()
        return res
