# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import ckan.controllers.organization as organization
import ckan.controllers.group as group
import ckan.lib.base as base
import ckan.lib.helpers as h
import ckan.logic as logic
import ckan.authz as authz
import ckan.model as model
from ckan.common import OrderedDict, c, g, request, _
import ckanext.gov_theme.base as custom_base
import ckan.lib.navl.dictization_functions as dict_fns
import ckanext.custom_google_analytics.helpers as analytics_helpers

render = base.render
abort = base.abort
NotAuthorized = logic.NotAuthorized
NotFound = logic.NotFound
ValidationError = logic.ValidationError
get_action = logic.get_action
tuplize_dict = logic.tuplize_dict
clean_dict = logic.clean_dict
parse_params = logic.parse_params
check_access = logic.check_access

class CustomOrganizationController(organization.OrganizationController, group.GroupController):

    def index(self):

        #custom_base.g_analitics()
        analytics_helpers.reset_analytics_code()

        group_type = self._guess_group_type()

        page = h.get_page_number(request.params) or 1
        items_per_page = 21

        context = {'model': model, 'session': model.Session,
                   'user': c.user or c.author, 'for_view': True,
                   'with_private': False}

        q = c.q = request.params.get('q', '')
        sort_by = c.sort_by_selected = request.params.get('sort')
        empty_string = ""
        # default sort by number of organization's datasets
        if sort_by is None or sort_by == empty_string:
            sort_by = 'package_count desc'
        try:
            self._check_access('site_read', context)
        except NotAuthorized:
            abort(401, _('Not authorized to see this page'))

        # pass user info to context as needed to view private datasets of
        # orgs correctly
        if c.userobj:
            context['user_id'] = c.userobj.id
            context['user_is_admin'] = c.userobj.sysadmin

        data_dict_global_results = {
            'all_fields': False,
            'q': q,
            'sort': sort_by,
            'type': group_type or 'group',
        }
        global_results = self._action('group_list')(context,
                                                    data_dict_global_results)

        data_dict_page_results = {
            'all_fields': True,
            'q': q,
            'sort': sort_by,
            'type': group_type or 'group',
            'limit': items_per_page,
            'offset': items_per_page * (page - 1),
        }
        page_results = self._action('group_list')(context,
                                                  data_dict_page_results)

        c.page = h.Page(
            collection=global_results,
            page=page,
            url=h.pager_url,
            items_per_page=items_per_page,
        )

        c.page.items = page_results
        return render(self._index_template(group_type),
                      extra_vars={'group_type': group_type})

    def new(self, data=None, errors=None, error_summary=None):
        if data and 'type' in data:
            group_type = data['type']
        else:
            group_type = self._guess_group_type(True)
        if data:
            data['type'] = group_type

        context = {'model': model, 'session': model.Session,
                   'user': c.user or c.author,
                   'save': 'save' in request.params,
                   'parent': request.params.get('parent', None)}
        try:
            self._check_access('group_create', context)
        except NotAuthorized:
            abort(401, _('Unauthorized to create a group'))

        if context['save'] and not data:
            #check against csrf attacks
            custom_base.csrf_check(self)
            return self._save_new(context, group_type)

        data = data or {}
        if not data.get('image_url', '').startswith('http'):
            data.pop('image_url', None)

        errors = errors or {}
        error_summary = error_summary or {}
        vars = {'data': data, 'errors': errors,
                'error_summary': error_summary, 'action': 'new',
                'group_type': group_type}

        self._setup_template_variables(context, data, group_type=group_type)
        c.form = render(self._group_form(group_type=group_type),
                        extra_vars=vars)
        return render(self._new_template(group_type),
                      extra_vars={'group_type': group_type})

    def delete(self, id):
        group_type = self._ensure_controller_matches_group_type(id)

        if 'cancel' in request.params:
            h.redirect_to(group_type + '_edit', id=id)
            #self._redirect_to_this_controller(action='edit', id=id)

        context = {'model': model, 'session': model.Session,
                   'user': c.user or c.author}

        try:
            self._check_access('group_delete', context, {'id': id})
        except NotAuthorized:
            abort(401, _('Unauthorized to delete group %s') % '')

        try:
            if request.method == 'POST':
                #check against csrf attacks
                custom_base.csrf_check(self)
                self._action('group_delete')(context, {'id': id})
                if group_type == 'organization':
                    h.flash_notice(_('Organization has been deleted.'))
                elif group_type == 'group':
                    h.flash_notice(_('Group has been deleted.'))
                else:
                    h.flash_notice(_('%s has been deleted.')
                                   % _(group_type.capitalize()))
                h.redirect_to(group_type + '_index')
                #self._redirect_to_this_controller(action='index')
            c.group_dict = self._action('group_show')(context, {'id': id})
        except NotAuthorized:
            abort(401, _('Unauthorized to delete group %s') % '')
        except NotFound:
            abort(404, _('Group not found'))
        except ValidationError as e:
            h.flash_error(e.error_dict['message'])
            h.redirect_to(controller='organization', action='read', id=id)
        return self._render_template('group/confirm_delete.html', group_type)

    def read(self, id, limit=20):

        #custom_base.g_analitics()

        group_type = self._ensure_controller_matches_group_type(
            id.split('@')[0])

        context = {'model': model, 'session': model.Session,
                   'user': c.user or c.author,
                   'schema': self._db_to_form_schema(group_type=group_type),
                   'for_view': True}
        data_dict = {'id': id}

        # unicode format (decoded from utf8)
        c.q = request.params.get('q', '')

        try:
            # Do not query for the group datasets when dictizing, as they will
            # be ignored and get requested on the controller anyway
            data_dict['include_datasets'] = False
            c.group_dict = self._action('group_show')(context, data_dict)
            c.group = context['group']
        except NotFound:
            abort(404, _('Group not found'))
        except NotAuthorized:
            abort(401, _('Unauthorized to read group %s') % id)

        self._read(id, limit, group_type)

        analytics_helpers.update_analytics_code_by_organization(c.group_dict['id'])

        return render(self._read_template(c.group_dict['type']),
                      extra_vars={'group_type': group_type})

    def _read(self, id, limit, group_type):
        ''' This is common code used by both read and bulk_process'''
        context = {'model': model, 'session': model.Session,
                   'user': c.user,
                   'schema': self._db_to_form_schema(group_type=group_type),
                   'for_view': True, 'extras_as_string': True}

        q = c.q = request.params.get('q', '')

        #if q is not None and q.strip():
        #    q = 'text:{q}'.format(q=q)
        # Search within group
        if c.group_dict.get('is_organization'):
            fq = ' owner_org:"%s"' % c.group_dict.get('id')
        else:
            fq = ' groups:"%s"' % c.group_dict.get('name')

        c.description_formatted = \
            h.render_markdown(c.group_dict.get('description'))

        context['return_query'] = True

        page = h.get_page_number(request.params)

        # most search operations should reset the page counter:
        params_nopage = [(k, v) for k, v in request.params.items()
                         if k != 'page']
        sort_by = request.params.get('sort', None)

        def search_url(params):
            controller = group.lookup_group_controller(group_type)
            action = 'bulk_process' if c.action == 'bulk_process' else 'read'
            url = h.url_for(controller=controller, action=action, id=id)
            params = [(k, v.encode('utf-8') if isinstance(v, basestring)
                       else str(v)) for k, v in params]
            return url + u'?' + group.urlencode(params)

        def drill_down_url(**by):
            return h.add_url_param(alternative_url=None,
                                   controller='group', action='read',
                                   extras=dict(id=c.group_dict.get('name')),
                                   new_params=by)

        c.drill_down_url = drill_down_url

        def remove_field(key, value=None, replace=None):
            controller = group.lookup_group_controller(group_type)
            return h.remove_url_param(key, value=value, replace=replace,
                                      controller=controller, action='read',
                                      extras=dict(id=c.group_dict.get('name')))

        c.remove_field = remove_field

        def pager_url(q=None, page=None):
            params = list(params_nopage)
            params.append(('page', page))
            return search_url(params)

        try:
            c.fields = []
            c.fields_grouped = {}
            search_extras = {}
            ckan_default_search_params = ['tags','_tags_limit', 'organization', 'license_id']
            for (param, value) in request.params.items():
                if param not in ['q', 'page', 'sort'] \
                        and len(value) and not param.startswith('_'):
                    if not param.startswith('ext_'):
                        if param in ckan_default_search_params:
                            c.fields.append((param, value))
                            q += ' %s: "%s"' % (param, value)
                            if param not in c.fields_grouped:
                                c.fields_grouped[param] = [value]
                            else:
                                c.fields_grouped[param].append(value)
                    else:
                        search_extras[param] = value

            facets = OrderedDict()

            default_facet_titles = {'organization': _('Organizations'),
                                    'groups': _('Groups'),
                                    'tags': _('Tags'),
                                    'res_format': _('Formats'),
                                    'license_id': _('Licenses')}

            for facet in h.facets():
                if facet in default_facet_titles:
                    facets[facet] = default_facet_titles[facet]
                else:
                    facets[facet] = facet

            # Facet titles
            self._update_facet_titles(facets, group_type)

            c.facet_titles = facets

            data_dict = {
                'q': q,
                'fq': fq,
                'include_private': True,
                'facet.field': facets.keys(),
                'rows': limit,
                'sort': sort_by,
                'start': (page - 1) * limit,
                'extras': search_extras
            }

            context_ = dict((k, v) for (k, v) in context.items()
                            if k != 'schema')
            query = get_action('package_search')(context_, data_dict)

            c.page = h.Page(
                collection=query['results'],
                page=page,
                url=pager_url,
                item_count=query['count'],
                items_per_page=limit
            )

            c.group_dict['package_count'] = query['count']

            c.search_facets = query['search_facets']
            c.search_facets_limits = {}
            for facet in c.search_facets.keys():
                limit = int(request.params.get('_%s_limit' % facet,
                            group.config.get('search.facets.default', 10)))
                c.search_facets_limits[facet] = limit
            c.page.items = query['results']

            c.sort_by_selected = sort_by

        except group.search.SearchError, se:
            group.log.error('Group search error: %r', se.args)
            c.query_error = True
            c.page = h.Page(collection=[])

        self._setup_template_variables(context, {'id': id},
                                       group_type=group_type)

    def member_new(self, id):
        group_type = self._ensure_controller_matches_group_type(id)

        context = {'model': model, 'session': model.Session,
                   'user': c.user or c.author}

        #self._check_access('group_delete', context, {'id': id})
        try:
            data_dict = {'id': id}
            data_dict['include_datasets'] = False
            c.group_dict = self._action('group_show')(context, data_dict)
            c.roles = self._action('member_roles_list')(
                context, {'group_type': group_type}
            )

            if request.method == 'POST':
                data_dict = clean_dict(dict_fns.unflatten(
                    tuplize_dict(parse_params(request.params))))
                data_dict['id'] = id

                email = data_dict.get('email')

                if email:
                    users_model = context['model']
                    result = users_model.User.by_email(email)
                    if result:
                        message = _(u'User with this {email} email already exists.').format(
                            email=email)
                        raise ValidationError({'message': message}, error_summary=message)
                    else:
                        user_data_dict = {
                            'email': email,
                            'group_id': data_dict['id'],
                            'role': data_dict['role']
                        }
                        del data_dict['email']
                        user_dict = self._action('user_invite')(
                            context, user_data_dict)
                        data_dict['username'] = user_dict['name']

                c.group_dict = self._action('group_member_create')(
                    context, data_dict)
                h.redirect_to(group_type + '_members', id=id)
                #self._redirect_to_this_controller(action='members', id=id)
            else:
                user = request.params.get('user')
                if user:
                    c.user_dict = \
                        get_action('user_show')(context, {'id': user})
                    c.user_role = \
                        authz.users_role_for_group_or_org(id, user) or 'member'
                else:
                    c.user_role = 'member'
        except NotAuthorized:
            abort(401, _('Unauthorized to add member to group %s') % '')
        except NotFound:
            abort(404, _('Group not found'))
        except ValidationError, e:
            error_message = _('User not found')
            if(e.error_dict.get('username') is not None):
                error_message = e.error_dict.get('username')[0]
            #h.flash_error(e.error_summary)
            h.flash_error(error_message)
        return self._render_template('group/member_new.html', group_type)

    def members(self, id):
        group_type = self._ensure_controller_matches_group_type(id)

        context = {'model': model, 'session': model.Session,
                   'user': c.user}

        try:
            data_dict = {'id': id}
            check_access('group_edit_permissions', context, data_dict)
            c.members = self._action('member_list')(
                context, {'id': id, 'object_type': 'user'}
            )
            data_dict['include_datasets'] = False
            c.group_dict = self._action('group_show')(context, data_dict)
        except NotFound:
            abort(404, _('Group not found'))
        except NotAuthorized:
            abort(
                403,
                _('User %r not authorized to edit members of %s') % (
                    c.user, id))

        return self._render_template('group/members.html', group_type)
