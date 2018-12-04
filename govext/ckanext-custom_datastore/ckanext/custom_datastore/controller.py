# encoding: utf-8
import urllib
import urlparse
import logging
import datetime

import sys
from ckan.plugins.toolkit import (
    Invalid,
    ObjectNotFound,
    NotAuthorized,
    get_action,
    get_validator,
    _,
    request,
    response,
    BaseController,
    abort,
    render,
    c,
    h
)
from ckanext.datastore.writer import (
    csv_writer,
    tsv_writer,
    json_writer,
    xml_writer,
)
from ckan.logic import (
    tuplize_dict,
    parse_params,
)

from ckan.controllers.api import ApiController

import ckan.lib.navl.dictization_functions as dict_fns

from itertools import izip_longest

int_validator = get_validator('int_validator')
boolean_validator = get_validator('boolean_validator')

DUMP_FORMATS = 'csv', 'tsv', 'json', 'xml'
PAGINATE_BY = 32000
logger = logging.getLogger(__name__)

import ckan.plugins.toolkit as toolkit
import json
import pylons
from pylons import request
import pylons.config as config
from ckan.common import request

import socket
import ckan.lib.base as base
import ckan.logic as logic
NotFound = logic.NotFound

def parseBoolString(theString = 'False'):
  return theString[0].upper()== 'T'

class DatastoreController(ApiController):


    def apiCheck(self, environ, start_response):
        logger.info("apiCheck start: %s ", str(datetime.datetime.time(datetime.datetime.now())))
        #return (self, environ, start_response)
        #return base.BaseController.__call__(self, environ, start_response)
        setWho = 'system'
        path_info = environ['PATH_INFO'].split("/")
        actionApi = path_info[-1]

        logger.info("action api is: %s", actionApi)

        ckan_site_local_url =  config.get('ckan.site_local_url')

        remoteAddress = ""
        try:
            remoteAddress = toolkit.request.environ['REMOTE_ADDR']
            ServerAddress = toolkit.request.environ['HTTP_HOST']
        except:
            remoteAddress = "No REMOTE_ADDR"

        logger.info("ServerAddress = %s", ServerAddress)
        logger.info("remoteAddress = %s", remoteAddress)

        try:
            backFlag = parseBoolString(config.get('ckan.gov_theme.is_back', False));
        except:
            backFlag = False

        socket_check_by_ip = "access_denied"
        try:
            logger.info("BEFORE socket.gethostbyaddr: %s ", str(datetime.datetime.time(datetime.datetime.now())))
            if remoteAddress ==  ckan_site_local_url:
                logger.info("INTERNAL API REQUEST, the action is: %s", actionApi)
                socketGetbyIP = socket.gethostbyaddr(remoteAddress)
                socket_check_by_ip = socketGetbyIP[0]
                logger.info("AFTER socket.gethostbyaddr: %s ", str(datetime.datetime.time(datetime.datetime.now())))
            else:
                socketGetbyIP = "denied"
                socket_check_by_ip = socketGetbyIP
                logger.info("socketGetbyIP = %s", socketGetbyIP)
        except Exception, ex:
            logger.error(ex.message)
            logger.info("BEFORE socket.getfqdn: %s ", str(datetime.datetime.time(datetime.datetime.now())))
            socketGetbyIP = socket.getfqdn()
            socket_check_by_ip = socketGetbyIP
            logger.info("AFTER socket.getfqdn: %s ", str(datetime.datetime.time(datetime.datetime.now())))


        #logger.info("INapiCheck: RemoteAddress = " + remoteAddress + " ServerAddress= " + ServerAddress + " API: " + actionApi + " backFlag = " + str(backFlag) + " socketGetbyIP= " +  socketGetbyIP[0] )
        logger.info("socketGetbyIP = %s", socketGetbyIP)
        logger.info("socket_check_by_ip = %s", socket_check_by_ip)



        if not backFlag:
            logger.info("if not backFlag: %s", str(not backFlag))
            if not socket_check_by_ip in ServerAddress:
                logger.info("if not socket_check_by_ip in ServerAddress: %s", str(not socket_check_by_ip in ServerAddress))
                if remoteAddress not in ServerAddress:
                    logger.info("remoteAddress not in ServerAddress: %s", str(remoteAddress not in ServerAddress))
                    setWho = 'user'
                    logger.info("BEFORE if config.get(ckan.api.open, NotInList).find(actionApi) < 0: %s ", str(datetime.datetime.time(datetime.datetime.now())))
                    if config.get('ckan.api.open', 'NotInList').find(actionApi) < 0:
                        logger.info("AFTER if config.get(ckan.api.open, NotInList).find(actionApi) < 0: %s ", str(datetime.datetime.time(datetime.datetime.now())))
                        return_dict = {}
                        return_dict['error'] = {'__type': 'Authorization Error',
                                                'message': _('Access denied')}
                        return_dict['success'] = False
                        logger.error(
                            "Access denied RemoteAddress = " + remoteAddress + " ServerAddress= " + ServerAddress + " API: " + actionApi + " socket_check_by_ip = " + socket_check_by_ip)
                        return self._finish(403, return_dict, content_type='json')
        else:
            setWho = 'Back'

        try:
            logger.info("BEFORE request_data = self._get_request_data(True): %s ", str(datetime.datetime.time(datetime.datetime.now())))
            request_data = self._get_request_data(True)
            logger.info("AFTER request_data = self._get_request_data(True): %s ",
                        str(datetime.datetime.time(datetime.datetime.now())))
        except Exception as e:
            return_dict = {}
            return_dict['success'] = False
            return_dict['__type'] = 'Error'
            return_dict['message'] = e.message
            return self._finish(404, return_dict, content_type='json')


        try:
            helpStr = h.url_for(controller='api',
                                action='action',
                                logic_function='help_show',
                                ver='3',
                                name=actionApi,
                                qualified=True, )
            return_dict = {'help': helpStr}
        except:
            helpStr = ""

        try:
            logger.info("BEFORE members: %s ", str(datetime.datetime.time(datetime.datetime.now())))
            #logger.warning("INapiCheck: About to run API: " + actionApi + "For sytem: " + setWho )
            members = toolkit.get_action(actionApi)(context = environ , data_dict=request_data)
            #logger.info("Run api successfuly " )
            logger.info("AFTER members: %s ", str(datetime.datetime.time(datetime.datetime.now())))
            return_dict['success'] = True
            return_dict['result'] =  members
            return self._finish_ok(return_dict)


        except Exception as e:
            logger.debug("INapiCheck API: " + actionApi + "For sytem: " + setWho )
            return_dict['success'] = False
            return_dict['__type'] = 'Error'
            try:
                return_dict['message'] = e.error_dict
            except:
                return_dict['message'] = e.message
                #return json.dumps({'help': helpStr, 'success': False,  'msg': e.error_dict  })
            return self._finish(404, return_dict, content_type='json')
                #return json.dumps({'help': helpStr, 'success': False, 'msg': e.message})



    def dump(self, resource_id):
        try:
            offset = int_validator(request.GET.get('offset', 0), {})
        except Invalid as e:
            abort(400, u'offset: ' + e.error)
        try:
            limit = int_validator(request.GET.get('limit'), {})
        except Invalid as e:
            abort(400, u'limit: ' + e.error)
        bom = boolean_validator(request.GET.get('bom'), {})
        fmt = request.GET.get('format', 'csv')

        if fmt not in DUMP_FORMATS:
            abort(400, _(
                u'format: must be one of %s') % u', '.join(DUMP_FORMATS))

        try:
            dump_to(
                resource_id,
                response,
                fmt=fmt,
                offset=offset,
                limit=limit,
                options={u'bom': bom})
        except ObjectNotFound:
            abort(404, _('DataStore resource not found'))

    def dictionary(self, id, resource_id):
        u'''data dictionary view: show/edit field labels and descriptions'''

        try:
            # resource_edit_base template uses these
            c.pkg_dict = get_action('package_show')(
                None, {'id': id})
            c.resource = get_action('resource_show')(
                None, {'id': resource_id})
            rec = get_action('datastore_search')(None, {
                'resource_id': resource_id,
                'limit': 0})
        except (ObjectNotFound, NotAuthorized):
            abort(404, _('Resource not found'))

        fields = [f for f in rec['fields'] if not f['id'].startswith('_')]

        if request.method == 'POST':
            data = dict_fns.unflatten(tuplize_dict(parse_params(
                request.params)))
            info = data.get(u'info')
            if not isinstance(info, list):
                info = []
            info = info[:len(fields)]

            get_action('datastore_create')(None, {
                'resource_id': resource_id,
                'force': True,
                'fields': [{
                    'id': f['id'],
                    'type': f['type'],
                    'info': fi if isinstance(fi, dict) else {}
                    } for f, fi in izip_longest(fields, info)]})

            h.redirect_to(
                controller='ckanext.datastore.controller:DatastoreController',
                action='dictionary',
                id=id,
                resource_id=resource_id)

        return render(
            'datastore/dictionary.html',
            extra_vars={'fields': fields})


def dump_to(resource_id, output, fmt, offset, limit, options):
    if fmt == 'csv':
        writer_factory = csv_writer
        records_format = 'csv'
    elif fmt == 'tsv':
        writer_factory = tsv_writer
        records_format = 'tsv'
    elif fmt == 'json':
        writer_factory = json_writer
        records_format = 'lists'
    elif fmt == 'xml':
        writer_factory = xml_writer
        records_format = 'objects'

    def start_writer(fields):
        bom = options.get(u'bom', False)
        return writer_factory(output, fields, resource_id, bom)

    def result_page(offs, lim):
        return get_action('datastore_search')(None, {
            'resource_id': resource_id,
            'limit':
                PAGINATE_BY if limit is None
                else min(PAGINATE_BY, lim),
            'offset': offs,
            'records_format': records_format,
            'include_total': 'false',  # XXX: default() is broken
        })

    result = result_page(offset, limit)

    with start_writer(result['fields']) as wr:
        while True:
            if limit is not None and limit <= 0:
                break

            records = result['records']

            wr.write_records(records)

            if records_format == 'objects' or records_format == 'lists':
                if len(records) < PAGINATE_BY:
                    break
            elif not records:
                break

            offset += PAGINATE_BY
            if limit is not None:
                limit -= PAGINATE_BY
                if limit <= 0:
                    break

            result = result_page(offset, limit)
