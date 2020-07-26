from ckan.controllers.api import ApiController
import logging
import datetime
import pylons.config as config
import ckan.plugins.toolkit as toolkit
from ckan.plugins.toolkit import (h, _)
from netaddr import IPNetwork, IPAddress

logger = logging.getLogger(__name__)


def parseBoolString(theString='False'):
    return theString[0].upper() == 'T'

class ApiUtilController(ApiController):



    def apiCheck(self, environ, start_response):
        logger.info("apiCheck start: %s ", str(datetime.datetime.time(datetime.datetime.now())))

        setWho = 'system'
        path_info = environ['PATH_INFO'].split("/")
        actionApi = path_info[-1]

        logger.info("action api is: %s", actionApi)

        try:
            backFlag = parseBoolString(config.get('ckan.gov_theme.is_back', False))
        except:
            backFlag = False

        if not backFlag:
            logger.info("if not backFlag: %s", str(not backFlag))

            http_real_address = config.get('ckan.http_real_address')

            logger.info(toolkit.request.environ)
            try:
                remoteAddress = toolkit.request.environ['REMOTE_ADDR']
            except:
                remoteAddress = "No REMOTE_ADDR"
            try:
                realAddress = toolkit.request.environ['HTTP_X_REAL_IP']
            except:
                realAddress = "No REAL_ADDR"

            logger.info("remoteAddress = %s", remoteAddress)
            logger.info("realAddress = %s", realAddress)
            try:
                is_internal_ckan_request = ((str(realAddress) == http_real_address))
            except:
                is_internal_ckan_request = False

            logger.info("Is INTERNAL CKAN REQUEST: " + str(is_internal_ckan_request))

            if not is_internal_ckan_request:
                setWho = 'user'
                if config.get('ckan.api.open', 'NotInList').find(actionApi) < 0:
                    return_dict = {}
                    return_dict['error'] = {'__type': 'Authorization Error',
                                            'message': _('Access denied')}
                    return_dict['success'] = False
                    logger.error("Access denied RemoteAddress = " + remoteAddress + " , API: " + actionApi + ", RealAddress: "+ realAddress)
                    return self._finish(403, return_dict, content_type='json')
        else:
            setWho = 'Back'
        try:
            request_data = self._get_request_data(True)
            logger.info("request_data")
            logger.info(request_data)
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
            logger.info("INapiCheck: About to run API: " + actionApi + ", For sytem: " + setWho )
            data = toolkit.get_action(actionApi)(context=environ, data_dict=request_data)
            logger.info("Run api successfuly " )
            return_dict['success'] = True
            return_dict['result'] = data
            return self._finish_ok(return_dict)

        except Exception as e:
            logger.debug("INapiCheck API Error: for action: " + actionApi + ", For sytem: " + setWho + ", Error message: " + e.message)
            return_dict['success'] = False
            return_dict['__type'] = 'Error'
            try:
                return_dict['message'] = e.error_dict
            except:
                return_dict['message'] = e.message
                # return json.dumps({'help': helpStr, 'success': False,  'msg': e.error_dict  })
            return self._finish(404, return_dict, content_type='json')
            # return json.dumps({'help': helpStr, 'success': False, 'msg': e.message})
