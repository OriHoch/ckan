# encoding: utf-8
import logging
from ckan.common import config
from suds.client import Client

log = logging.getLogger(__name__)

def check_recaptcha(request):
    captcha_response = request.POST.get('g-recaptcha-response', None)
    application_id = str(config.get('ckan.recaptcha.application_id', ''))
    recaptcha_server_name = config.get('ckan.recaptcha.server_name')
    token_type = str(config.get('ckan.recaptcha.token_type'))
    appID_type = str(config.get('ckan.recaptcha.appID_type'))

    client = Client(recaptcha_server_name)
    log.info(client)
    token = client.factory.create(token_type)
    token.IDToken = captcha_response
    appID = client.factory.create(appID_type)
    appID = application_id

    r = client.service.ValidateCaptchaByAppId(token, appID)

    if r != None:
        message = r['Message']
        if message == "Valid":
            return True
        else:
            return False
    else:
        return False


class CaptchaError(ValueError):
    pass
