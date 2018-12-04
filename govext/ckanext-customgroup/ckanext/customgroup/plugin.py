import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit


class CustomGroupPlugin(plugins.SingletonPlugin):
    plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.IRoutes, inherit=True)

    # IConfigurer
    def update_config(self, config_):
        toolkit.add_template_directory(config_, 'templates')
        toolkit.add_public_directory(config_, 'public')
        toolkit.add_resource('fanstatic', 'customgroup')

    ## IRoutes
    def before_map(self, map):
        custom_group_controller = 'ckanext.customgroup.customgroup:CustomGroupController'
        map.connect('group_new', '/group/new',
                    controller=custom_group_controller,
                    action='new'),
        map.connect('group_delete', '/group/delete/{id}',
                    controller=custom_group_controller,
                    action='delete')

        return map
