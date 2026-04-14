# -*- coding: utf-8 -*-
from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class CleaningSite(models.Model):
    _name = 'cleaning.site'
    _description = 'Cleaning Site'
    _order = 'name'

    name = fields.Char(required=True)
    active = fields.Boolean(default=True)
    partner_id = fields.Many2one(
        'res.partner',
        string='Customer',
        help='Customer/contact linked to this cleaning site.',
    )
    street = fields.Char()
    street2 = fields.Char()
    city = fields.Char()
    state_id = fields.Many2one('res.country.state', string='State')
    zip = fields.Char(string='ZIP')
    country_id = fields.Many2one('res.country', string='Country')
    qr_reference = fields.Char(
        string='QR Reference',
        help='Short identifier printed near the QR code for this site.',
    )
    qr_ready = fields.Boolean(
        string='QR Ready',
        compute='_compute_qr_ready',
        store=True,
        help='True when the site has enough data for practical QR usage in the demo.',
    )
    qr_readiness_note = fields.Char(
        string='QR Readiness Note',
        compute='_compute_qr_readiness_note',
    )
    fsm_portal_site_qr_url = fields.Char(
        string='Site QR Entry URL',
        compute='_compute_fsm_portal_site_qr_url',
        help='Site-oriented QR URL. Cleaner scans at site, logs in, then sees only their site visits.',
    )
    note = fields.Text()
    task_ids = fields.One2many('project.task', 'fsm_cleaning_site_id', string='Visits')
    task_count = fields.Integer(compute='_compute_task_count')
    fsm_allowed_cleaner_ids = fields.Many2many(
        'res.users',
        'cleaning_site_res_users_rel',
        'site_id',
        'user_id',
        string='Allowed Cleaners',
        domain="[('share', '=', True), ('active', '=', True)]",
        help='Portal cleaners who can be assigned to visits for this site.',
    )

    @api.depends('task_ids')
    def _compute_task_count(self):
        grouped = self.env['project.task'].read_group(
            [('fsm_cleaning_site_id', 'in', self.ids)],
            ['fsm_cleaning_site_id'],
            ['fsm_cleaning_site_id'],
        )
        counts = {
            row['fsm_cleaning_site_id'][0]: row['fsm_cleaning_site_id_count']
            for row in grouped if row.get('fsm_cleaning_site_id')
        }
        for site in self:
            site.task_count = counts.get(site.id, 0)

    @api.depends('name', 'partner_id', 'street', 'city', 'country_id', 'qr_reference')
    def _compute_qr_ready(self):
        for site in self:
            site.qr_ready = site._get_qr_readiness_data()[0]

    @api.depends('name', 'partner_id', 'street', 'city', 'country_id', 'qr_reference')
    def _compute_qr_readiness_note(self):
        for site in self:
            site.qr_readiness_note = site._get_qr_readiness_data()[1]

    def _get_qr_readiness_data(self):
        self.ensure_one()
        has_address = bool(self.street or self.city or self.country_id)
        has_partner = bool(self.partner_id)
        if not self.name:
            return False, _('Missing site name.')
        if has_partner or has_address:
            if self.qr_reference:
                return True, _('Ready: site details and QR reference are set.')
            return True, _('Ready: site details are set (QR reference optional).')
        return False, _('Add customer or address details to make this site QR-ready.')

    @api.depends('active', 'name', 'qr_reference')
    def _compute_fsm_portal_site_qr_url(self):
        base = self.env['ir.config_parameter'].sudo().get_param('web.base.url', '').rstrip('/')
        for site in self:
            if base and site.id and site.active:
                site.fsm_portal_site_qr_url = '%s/my/fsm-site/%s' % (base, int(site.id))
            else:
                site.fsm_portal_site_qr_url = False

    @api.onchange('partner_id')
    def _onchange_partner_id_address(self):
        if not self.partner_id:
            return
        partner = self.partner_id
        if not self.street:
            self.street = partner.street
        if not self.street2:
            self.street2 = partner.street2
        if not self.city:
            self.city = partner.city
        if not self.state_id:
            self.state_id = partner.state_id
        if not self.zip:
            self.zip = partner.zip
        if not self.country_id:
            self.country_id = partner.country_id

    def action_open_site_visits(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Site Visits'),
            'res_model': 'project.task',
            'view_mode': 'list,form,kanban,calendar,pivot,graph',
            'domain': [('fsm_cleaning_site_id', '=', self.id)],
            'context': {
                'search_default_open_tasks': 1,
                'default_fsm_cleaning_site_id': self.id,
                'default_is_fsm': True,
            },
        }

    def action_open_site_qr_png(self):
        self.ensure_one()
        if not self.fsm_portal_site_qr_url:
            return False
        return {
            'type': 'ir.actions.act_url',
            'url': '/cleaning_fsm_portal/site_qr_png/%s' % int(self.id),
            'target': 'new',
        }

    @api.constrains('fsm_allowed_cleaner_ids')
    def _check_fsm_allowed_cleaners_are_portal_users(self):
        for site in self:
            for user in site.fsm_allowed_cleaner_ids:
                if not user.active or not user.share or not user.has_group('base.group_portal'):
                    raise ValidationError(
                        _('Allowed cleaners must be active portal users.')
                    )
