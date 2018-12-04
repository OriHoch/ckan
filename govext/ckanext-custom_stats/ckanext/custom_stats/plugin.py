from logging import getLogger

import ckan.plugins as p

log = getLogger(__name__)

class StatsPlugin(p.SingletonPlugin):
    '''Stats plugin.'''

    p.implements(p.IRoutes, inherit=True)
    p.implements(p.IConfigurer, inherit=True)

    def after_map(self, map):
        custom_stats_controller = 'ckanext.custom_stats.controller:StatsController'
        map.connect('stats', '/stats',
            controller=custom_stats_controller,
            action='index')
        map.connect('stats_action', '/stats/{action}',
            controller=custom_stats_controller)
        return map

    def update_config(self, config):
        templates = 'templates'
        if p.toolkit.asbool(config.get('ckan.legacy_templates', False)):
                templates = 'templates_legacy'
        p.toolkit.add_template_directory(config, templates)
        p.toolkit.add_public_directory(config, 'public')
        p.toolkit.add_resource('public/ckanext/stats', 'ckanext_stats')
