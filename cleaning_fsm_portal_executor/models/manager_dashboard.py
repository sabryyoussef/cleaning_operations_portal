# -*- coding: utf-8 -*-
from markupsafe import Markup, escape
from collections import Counter

from odoo import _, api, fields, models


class CleaningFsmManagerDashboard(models.Model):
    _name = 'cleaning.fsm.manager.dashboard'
    _description = 'Cleaning FSM Manager Dashboard'

    name = fields.Char(required=True)
    refreshed_at = fields.Datetime(compute='_compute_metrics')
    total_visits = fields.Integer(compute='_compute_metrics')
    not_started_visits = fields.Integer(compute='_compute_metrics')
    in_progress_visits = fields.Integer(compute='_compute_metrics')
    completed_visits = fields.Integer(compute='_compute_metrics')
    late_checkins = fields.Integer(compute='_compute_metrics')
    by_cleaner_html = fields.Html(compute='_compute_metrics', sanitize=False)
    by_site_html = fields.Html(compute='_compute_metrics', sanitize=False)

    def _fsm_base_domain(self):
        return [('is_fsm', '=', True)]

    def _render_group_table(self, rows, title, bg_color, border_color, title_color):
        if not rows:
            return Markup(
                '<div class="rounded p-3" style="background:%s; border:1px solid %s;">'
                '<h5 class="mb-2" style="color:%s;">%s</h5>'
                '<p class="text-muted mb-0">%s</p>'
                '</div>'
            ) % (
                escape(bg_color),
                escape(border_color),
                escape(title_color),
                escape(title),
                escape(_('No data yet.')),
            )
        body = ''.join(
            '<tr><td>%s</td><td class="text-end">%s</td></tr>' % (
                escape(label),
                int(count),
            )
            for label, count in rows
        )
        return Markup(
            '<div class="rounded p-3 h-100" style="background:%s; border:1px solid %s;">'
            '<h5 class="mb-2" style="color:%s;">%s</h5>'
            '<table class="table table-sm table-hover align-middle mb-0">'
            '<thead><tr><th>%s</th><th class="text-end">%s</th></tr></thead>'
            '<tbody>%s</tbody></table></div>'
        ) % (
            escape(bg_color),
            escape(border_color),
            escape(title_color),
            escape(title),
            escape(_('Group')),
            escape(_('Visits')),
            Markup(body),
        )

    @api.depends_context('uid')
    def _compute_metrics(self):
        Task = self.env['project.task']
        base_domain = self._fsm_base_domain()

        tasks = Task.search(base_domain)

        total = len(tasks)
        not_started = sum(1 for t in tasks if not t.fsm_portal_started_at)
        in_progress = sum(1 for t in tasks if t.fsm_portal_started_at and not t.fsm_portal_ended_at)
        completed = sum(1 for t in tasks if t.fsm_portal_ended_at)
        late = sum(1 for t in tasks if t.fsm_portal_late_start)

        cleaner_counter = Counter(
            t.fsm_portal_executor_id.display_name
            for t in tasks if t.fsm_portal_executor_id
        )
        cleaner_rows = cleaner_counter.most_common(8)

        site_counter = Counter(
            t.fsm_cleaning_site_id.display_name
            for t in tasks if t.fsm_cleaning_site_id
        )
        site_rows = site_counter.most_common(8)

        for rec in self:
            rec.refreshed_at = fields.Datetime.now()
            rec.total_visits = total
            rec.not_started_visits = not_started
            rec.in_progress_visits = in_progress
            rec.completed_visits = completed
            rec.late_checkins = late
            rec.by_cleaner_html = self._render_group_table(
                cleaner_rows,
                _('Top cleaners by visit volume'),
                '#f8fafc',
                '#cbd5e1',
                '#1d4ed8',
            )
            rec.by_site_html = self._render_group_table(
                site_rows,
                _('Top sites by visit volume'),
                '#f0fdf4',
                '#bbf7d0',
                '#166534',
            )

    def _open_tasks(self, extra_domain=None):
        self.ensure_one()
        domain = self._fsm_base_domain() + (extra_domain or [])
        return {
            'type': 'ir.actions.act_window',
            'name': _('FSM Visits'),
            'res_model': 'project.task',
            'view_mode': 'list,kanban,form,pivot,graph,calendar',
            'domain': domain,
            'context': {
                'search_default_open_tasks': 1,
                'default_is_fsm': True,
            },
        }

    def action_open_all(self):
        return self._open_tasks()

    def action_open_not_started(self):
        return self._open_tasks([('fsm_portal_started_at', '=', False)])

    def action_open_in_progress(self):
        return self._open_tasks([('fsm_portal_started_at', '!=', False), ('fsm_portal_ended_at', '=', False)])

    def action_open_completed(self):
        return self._open_tasks([('fsm_portal_ended_at', '!=', False)])

    def action_open_late(self):
        return self._open_tasks([('fsm_portal_late_start', '=', True)])

    def action_refresh_dashboard(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'cleaning.fsm.manager.dashboard',
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'current',
        }
