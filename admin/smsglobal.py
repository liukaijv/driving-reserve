#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""SMS Global sms backend class."""
from django.conf import settings
import urllib2
import urllib
import json
from xml.etree import ElementTree
import logging

logger = logging.getLogger(__name__)

SMSGLOBAL_USERNAME = getattr(settings, 'SMSGLOBAL_USERNAME', '')
SMSGLOBAL_PASSWORD = getattr(settings, 'SMSGLOBAL_PASSWORD', '')
SMSGLOBAL_API_URL_SENDSMS = getattr(settings, 'SMSGLOBAL_API_URL_SENDSMS', '')
SMSGLOBAL_API_URL_CHECKBALANCE = getattr(settings, 'SMSGLOBAL_API_URL_CHECKBALANCE', '')


class SmsBackend(object):
    def get_username(self):
        return SMSGLOBAL_USERNAME

    def get_password(self):
        return SMSGLOBAL_PASSWORD

    def get_balance(self):
        params = {
            'cdkey': self.get_username(),
            'password': self.get_password(),
            'type': 'xml',
        }

        req = urllib2.Request(SMSGLOBAL_API_URL_CHECKBALANCE, urllib.urlencode(params))
        response = urllib2.urlopen(req).read()
        code, msg = self._parse_xml_response(response)
        return msg


    def send_messages(self, to=None, body=None):
        """A helper method that does the actual sending."""
        type = 'xml'
        params = {
            'cdkey': self.get_username(),
            'password': self.get_password(),
            'phone': ",".join(to),
            'message': body,
            'type': type,
        }

        req = urllib2.Request(SMSGLOBAL_API_URL_SENDSMS, urllib.urlencode(params))
        result_page = urllib2.urlopen(req).read()
        results = self._parse_xml_response(result_page)
        code, msg = results
        if code != '0':
            logger.info('SENT to: %s; code: %s; msg: %s; message: %s' % (
                to, code, msg, body))
            return False
        else:
            return True

    def _parse_response(self, result_page):
        result = json.loads(result_page, encoding='utf-8')
        if result:
            return (result['code'], result['msg'])
        return None

    def _parse_xml_response(self, result_page):
        etree = ElementTree.fromstring(result_page.strip())
        if etree:
            return (etree[0].text, etree[1].text)
        return None


class LetterBackend(object):
    pass