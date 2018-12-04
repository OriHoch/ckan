import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit


class CustomOrganizationPlugin(plugins.SingletonPlugin):
    plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.IRoutes, inherit=True)

    # IConfigurer
    def update_config(self, config_):
        toolkit.add_template_directory(config_, 'templates')
        toolkit.add_public_directory(config_, 'public')
        toolkit.add_resource('fanstatic', 'customorganization')

    ## IRoutes
    def before_map(self, map):
        custom_org_controller = 'ckanext.customorganization.customorganization:CustomOrganizationController'
        map.connect('organizations_index', '/organization',
                    controller=custom_org_controller,
                    action='index'),
        map.connect('/organization/new',
                    controller=custom_org_controller,
                    action='new'),
        map.connect('organization_read', '/organization/{id}',
                    controller=custom_org_controller,
                    action='read'),
        map.connect('/organization/delete/{id}',
                    controller=custom_org_controller,
                    action='delete'),
        map.connect('/organization/member_new/{id}',
                    controller=custom_org_controller,
                    action='member_new')
        map.connect('/organization/members/{id}',
                    controller=custom_org_controller,
                    action='members')
        return map
