import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit


class CustomAdminPlugin(plugins.SingletonPlugin):
    plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.IRoutes, inherit=True)

    # IConfigurer
    def update_config(self, config_):
        toolkit.add_template_directory(config_, 'templates')
        toolkit.add_public_directory(config_, 'public')
        toolkit.add_resource('fanstatic', 'customadmin')

    ## IRoutes
    def before_map(self, map):
        custom_admin_controller = 'ckanext.customadmin.customadmin:CustomAdminController'
        map.connect('ckanadmin_config', '/ckan-admin/config',
                    controller=custom_admin_controller,
                    action='config', ckan_icon='check')
        map.connect('/ckan-admin/reset_config',
                    controller=custom_admin_controller,
                    action='reset_config', ckan_icon='check')

        return map
