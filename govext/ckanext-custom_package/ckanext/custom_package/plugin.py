import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit


class Custom_PackagePlugin(plugins.SingletonPlugin):
    plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.IRoutes, inherit=True)

    # IConfigurer

    def update_config(self, config_):
        toolkit.add_template_directory(config_, 'templates')
        toolkit.add_public_directory(config_, 'public')
        toolkit.add_resource('fanstatic', 'custom_package')

    ## IRoutes
    def before_map(self, map):
        custom_controller = 'ckanext.custom_package.custom_package:CustomPackageController'
        map.connect('add dataset', '/dataset/new',
                    controller=custom_controller,
                    action='new')
        map.connect('/dataset',
                    controller=custom_controller,
                    action='search')
        map.connect('/dataset/{id}',
                    controller=custom_controller,
                    action='read')
        map.connect('/dataset/new_resource/{id}',
                    controller=custom_controller,
                    action='new_resource')
        map.connect('/dataset/{id}/resource/{resource_id}',
                    controller=custom_controller,
                    action='resource_read')
        map.connect('/dataset/{id}/resource/{resource_id}/download',
                    controller=custom_controller,
                    action='resource_download')
        map.connect('/dataset/{id}/resource/{resource_id}/download/{filename}',
                    controller=custom_controller,
                    action='resource_download')
        map.connect('resource_edit', '/dataset/{id}/resource_edit/{resource_id}',
                    controller=custom_controller,
                    action='resource_edit', ckan_icon='edit')
        map.connect('dataset_edit', '/dataset/edit/{id}', action='edit',
                    controller=custom_controller,
                    ckan_icon='edit')
        map.connect('/dataset/{id}/resource_delete/{resource_id}',
                    controller=custom_controller,
                    action='resource_delete')
        map.connect('/dataset/delete/{id}',
                    controller=custom_controller,
                    action='delete')
        map.connect('/dataset/{id}/resource/{resource_id}/embed',
                    controller=custom_controller,
                    action='resource_embedded_dataviewer')
        map.connect('/dataset/{id}/resource/{resource_id}/viewer',
                    controller=custom_controller,
                    action='resource_embedded_dataviewer', width="960",
                    height="800")
        map.connect('views', '/dataset/{id}/resource/{resource_id}/views',
                    controller=custom_controller,
                    action='resource_views', ckan_icon='reorder')
        map.connect('new_view', '/dataset/{id}/resource/{resource_id}/new_view',
                    controller=custom_controller,
                    action='edit_view', ckan_icon='edit')
        map.connect('edit_view',
                    '/dataset/{id}/resource/{resource_id}/edit_view/{view_id}',
                    controller=custom_controller,
                    action='edit_view', ckan_icon='edit')
        map.connect('resource_view',
                    '/dataset/{id}/resource/{resource_id}/view/{view_id}',
                    controller=custom_controller,
                    action='resource_view')
        map.connect('/dataset/{id}/resource/{resource_id}/view/',
                    controller=custom_controller,
                    action='resource_view')
        map.connect('/dataset/{id}/resource/{resource_id}/preview',
                    controller=custom_controller,
                    action='resource_datapreview')
        return map
