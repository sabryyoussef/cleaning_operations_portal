# -*- coding: utf-8 -*-
{
    'name': 'Cleaning FSM Portal Executor',
    'version': '19.0.1.4.0',
    'category': 'Services/Field Service',
    'summary': 'Assign a portal cleaner to FSM tasks and confirm visit start from the portal',
    'description': """
Portal execution (v1)
=====================
* One portal cleaner per Field Service task (separate from internal assignees).
* Portal users read their assigned visits; only a dedicated controller can set "Visit started".
* Internal user_ids assignees are unchanged.
    """,
    'author': 'Cleaning POC',
    'license': 'LGPL-3',
    'depends': [
        'project',
        'portal',
        'industry_fsm',
    ],
    'data': [
        'security/fsm_portal_executor_security.xml',
        'security/ir.model.access.csv',
        'data/manager_dashboard_data.xml',
        'report/fsm_portal_visit_summary_report.xml',
        'views/manager_dashboard_views.xml',
        'views/cleaning_site_views.xml',
        'views/project_task_views.xml',
        'views/project_task_search_views.xml',
        'views/project_task_list_views.xml',
        'views/portal_templates.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            'cleaning_fsm_portal_executor/static/src/js/fsm_portal_start_visit_geo.js',
        ],
    },
    'installable': True,
    'application': False,
}
