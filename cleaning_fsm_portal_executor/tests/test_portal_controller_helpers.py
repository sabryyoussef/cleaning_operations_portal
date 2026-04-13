# -*- coding: utf-8 -*-
from odoo.tests import TransactionCase, tagged

from odoo.addons.cleaning_fsm_portal_executor.controllers import portal_fsm as pf


@tagged('post_install', '-at_install', 'cleaning_fsm_portal')
class TestPortalFsmHelpers(TransactionCase):
    """Pure helpers used by portal HTTP (no request object)."""

    def test_parse_optional_float(self):
        self.assertIsNone(pf._fsm_parse_optional_float(None))
        self.assertIsNone(pf._fsm_parse_optional_float(''))
        self.assertIsNone(pf._fsm_parse_optional_float('not-a-number'))
        self.assertEqual(pf._fsm_parse_optional_float('25.0765'), 25.0765)
        self.assertEqual(pf._fsm_parse_optional_float(12), 12.0)

    def test_geo_from_request_keys_ok_and_miss(self):
        form = {
            'fsm_portal_start_geo_lat': '25.0',
            'fsm_portal_start_geo_lon': '55.0',
            'fsm_portal_start_geo_accuracy': '12.5',
        }
        vals, flag = pf._fsm_portal_geo_from_request_keys(
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
        self.assertEqual(flag, 'ok')
        self.assertEqual(vals.get('fsm_portal_start_latitude'), 25.0)
        self.assertEqual(vals.get('fsm_portal_start_longitude'), 55.0)
        self.assertEqual(vals.get('fsm_portal_start_accuracy'), 12.5)

    def test_geo_from_request_keys_miss_without_coords(self):
        vals, flag = pf._fsm_portal_geo_from_request_keys(
            {},
            'lat_k',
            'lon_k',
            'acc_k',
            {'lat': 'fsm_portal_start_latitude', 'lon': 'fsm_portal_start_longitude', 'acc': 'fsm_portal_start_accuracy'},
        )
        self.assertEqual(flag, 'miss')
        self.assertFalse(vals)

    def test_geo_from_request_keys_invalid_lat_lon_range(self):
        form = {'fsm_portal_start_geo_lat': '200', 'fsm_portal_start_geo_lon': '55'}
        vals, flag = pf._fsm_portal_geo_from_request_keys(
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
        self.assertEqual(flag, 'miss')
        self.assertFalse(vals)
