import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit


class CustomUserPlugin(plugins.SingletonPlugin):
    plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.IRoutes, inherit=True)



    # IConfigurer
    def update_config(self, config_):
        toolkit.add_template_directory(config_, 'templates')
        toolkit.add_public_directory(config_, 'public')
        toolkit.add_resource('fanstatic', 'customuser')


    ## IRoutes
    def before_map(self, map):
        custom_user_controller = 'ckanext.customuser.customuser:CustomUserController'
        map.connect('/user/edit',
                    controller=custom_user_controller,
                    action='edit')
        map.connect('user_edit', '/user/edit/{id:.*}',
                    controller=custom_user_controller,
                    action='edit')
        map.connect('register', '/user/register',
                    controller=custom_user_controller,
                    action='register')
        map.connect('user_delete', '/user/delete/{id}',
                    controller=custom_user_controller,
                    action='delete')
        map.connect('login', '/user/login',
                    controller=custom_user_controller,
                    action='login')
        map.connect('/user/logged_in',
                    controller=custom_user_controller,
                    action='logged_in')
        map.connect('/user/_logout',
                    controller=custom_user_controller,
                    action='logout')
        map.connect('/user/reset',
                    controller=custom_user_controller,
                    action='request_reset')
        map.connect('/user/reset/{id:.*}',
                    controller=custom_user_controller,
                    action='perform_reset')

        return map


