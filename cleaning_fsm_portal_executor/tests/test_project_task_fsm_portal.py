# -*- coding: utf-8 -*-
import uuid

from odoo.exceptions import AccessError, ValidationError
from odoo.tests import new_test_user, tagged

from .common import CleaningFsmPortalCommon


@tagged('post_install', '-at_install', 'cleaning_fsm_portal')
class TestProjectTaskFsmPortal(CleaningFsmPortalCommon):
    """Computes, access, constraints, late chatter notice, QR action."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.Task = cls.env['project.task']
        _u = uuid.uuid4().hex[:10]
        cls.portal_cleaner = new_test_user(
            cls.env,
            login='fsm_portal_%s' % _u,
            groups='base.group_portal',
        )
        cls.portal_cleaner.write({'share': True})
        cls.internal_user = new_test_user(
            cls.env,
            login='fsm_internal_%s' % _u,
            groups='base.group_user',
        )
        cls.internal_user.write({'share': False})

    def _create_fsm_task(self, **vals):
        base = {
            'name': 'Test FSM visit',
            'project_id': self.fsm_project.id,
            'partner_id': self.partner.id,
        }
        base.update(vals)
        return self.Task.create(base)

    def test_qr_entry_url_contains_visit_and_site_query(self):
        task = self._create_fsm_task()
        self.assertTrue(task.fsm_portal_qr_entry_url)
        self.assertIn('/my/fsm-visit/%s' % task.id, task.fsm_portal_qr_entry_url)
        self.assertIn('site=%s' % self.partner.id, task.fsm_portal_qr_entry_url)

    def test_late_checkin_compute_not_late_when_on_time(self):
        task = self._create_fsm_task(
            planned_date_begin='2026-06-01 08:00:00',
            fsm_portal_started_at='2026-06-01 07:55:00',
        )
        self.assertFalse(task.fsm_portal_late_start)
        self.assertFalse(task.fsm_portal_late_start_delay_text)

    def test_late_checkin_compute_late(self):
        task = self._create_fsm_task(
            planned_date_begin='2026-06-01 08:00:00',
            fsm_portal_started_at='2026-06-01 08:18:00',
        )
        self.assertTrue(task.fsm_portal_late_start)
        self.assertTrue(task.fsm_portal_late_start_delay_text)

    def test_format_lateness_delay_branches(self):
        task = self._create_fsm_task()
        self.assertIn('min', task._format_fsm_portal_lateness_delay(60))
        self.assertIn('h', task._format_fsm_portal_lateness_delay(3600 + 120))

    def test_visit_duration_text_valid_and_invalid(self):
        task = self._create_fsm_task(
            fsm_portal_started_at='2026-06-01 10:00:00',
            fsm_portal_ended_at='2026-06-01 11:30:00',
        )
        self.assertTrue(task.fsm_portal_visit_duration_text)
        task2 = self._create_fsm_task(
            fsm_portal_started_at='2026-06-01 12:00:00',
            fsm_portal_ended_at='2026-06-01 11:00:00',
        )
        self.assertIn('Invalid', task2.fsm_portal_visit_duration_text or '')

    def test_portal_accessible_fields_include_fsm_portal_keys(self):
        readable, _w = self.Task._portal_accessible_fields()
        for fname in (
            'fsm_portal_photo_before',
            'fsm_portal_late_start',
            'fsm_portal_late_start_delay_text',
        ):
            self.assertIn(fname, readable)

    def test_fsm_portal_late_notice_not_in_portal_extra_readable_for_fields_get(self):
        """Internal flag must not be exposed to portal fields_get extra (avoid leaking / Owl noise)."""
        readable, _w = self.Task._portal_accessible_fields()
        self.assertNotIn('fsm_portal_late_notice_posted', readable)

    def test_executor_constraint_rejects_internal_user(self):
        task = self._create_fsm_task()
        with self.assertRaises(ValidationError):
            task.write({'fsm_portal_executor_id': self.internal_user.id})

    def test_executor_accepts_portal_user(self):
        task = self._create_fsm_task()
        task.write({'fsm_portal_executor_id': self.portal_cleaner.id})
        self.assertEqual(task.fsm_portal_executor_id, self.portal_cleaner)

    def test_portal_user_cannot_write_task_from_backend(self):
        task = self._create_fsm_task()
        with self.assertRaises(AccessError):
            task.with_user(self.portal_cleaner).write({'name': 'hacked'})

    def test_late_checkin_posts_chatter_note_once(self):
        msg_count_0 = self.env['mail.message'].search_count([('model', '=', 'project.task')])
        task = self._create_fsm_task(
            planned_date_begin='2026-06-10 09:00:00',
            fsm_portal_started_at='2026-06-10 09:25:00',
        )
        self.assertTrue(task.fsm_portal_late_start)
        self.assertTrue(task.fsm_portal_late_notice_posted)
        notes = task.message_ids.filtered(
            lambda m: m.message_type == 'notification' and m.subtype_id == self.env.ref('mail.mt_note')
        )
        self.assertTrue(notes, 'Expected at least one note from late check-in alert')
        msg_count_1 = self.env['mail.message'].search_count([('model', '=', 'project.task')])
        self.assertGreater(msg_count_1, msg_count_0)
        # Second write should not duplicate
        task.write({'name': 'Renamed only'})
        after_rename = task.message_ids.filtered(
            lambda m: 'Late check-in alert' in (m.body or '')
        )
        self.assertEqual(len(after_rename), 1)

    def test_action_fsm_open_qr_png_fsm(self):
        task = self._create_fsm_task()
        act = task.action_fsm_open_qr_png()
        self.assertEqual(act['type'], 'ir.actions.act_url')
        self.assertIn(str(task.id), act['url'])
        self.assertEqual(act['target'], 'new')

    def test_action_fsm_open_qr_png_non_fsm_returns_false(self):
        project = self.env['project.project'].create({
            'name': 'Non FSM',
            'is_fsm': False,
            'company_id': self.env.company.id,
        })
        task = self._create_fsm_task(project_id=project.id)
        self.assertFalse(task.action_fsm_open_qr_png())
