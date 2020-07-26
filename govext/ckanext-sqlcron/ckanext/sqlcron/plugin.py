import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit


class SqlcronPlugin(plugins.SingletonPlugin):
    plugins.implements(plugins.IConfigurer)

    # IConfigurer

    def update_config(self, config_):
        toolkit.add_template_directory(config_, 'templates')
        toolkit.add_public_directory(config_, 'public')
        toolkit.add_resource('fanstatic', 'sqlcron')

    ## IRoutes
    def before_map(self, map):
        custom_user_controller = 'ckanext.sqlcron.sqlcrn:sqlCronController'
        map.connect('/sqlcron',
                    controller=sql_cron_controller,
                    action='cron')

        return map
