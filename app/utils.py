# -*- coding: utf-8 -*-
from django.utils.functional import Promise
from django.utils.encoding import force_unicode
from django.forms.util import ErrorList

from admin.common import JsonResponse


try:
    from simplejson import JSONEncoder
except ImportError:
    try:
        from json import JSONEncoder
    except ImportError:
        from django.utils.simplejson import JSONEncoder


class LazyEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Promise):
            return force_unicode(obj)
        return obj


class CustomErrorList(ErrorList):
    def __str__(self):
        return self.as_divs()

    def __unicode__(self):
        return self.as_divs()

    def as_divs(self):
        if not self: return u''
        return u'<div class="errorlist">%s</div>' % ''.join([u'<div class="error">%s</div>' % e for e in self])


# 数据成功
def ajax_ok(data=None, message=None, code=0, *args, **kwargs):
    result = {
        'code': code,
        'msg': message,
        'data': data
    }
    result.update(kwargs)
    return JsonResponse(result)


# 数据失败
def ajax_fail(data=None, message=None, code=-1, *args, **kwargs):
    result = {
        'code': code,
        'msg': message,
        'data': data
    }
    result.update(kwargs)
    return JsonResponse(result)