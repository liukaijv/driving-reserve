#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.http import Http404, HttpResponseRedirect

# ajax 请求过滤
def ajax_request(view):
    def temp_view(request, *args, **kwargs):
        if not request.is_ajax():
            raise Http404('你的请求出错了！')
        return view(request, *args, **kwargs)

    return temp_view


# 是否必须学员登陆
def front_login_required(view):
    def temp_view(request, *args, **kwargs):
        if request.user.is_authenticated():
            if request.user.role_type == 1:
                return HttpResponseRedirect('/app/student_profile/')
            elif request.user.role_type == 2:
                return HttpResponseRedirect('/app/coach_profile/')
        return view(request, *args, **kwargs)

    return temp_view


# 是否必须学员登陆
def student_login_required(view):
    def temp_view(request, *args, **kwargs):
        if not request.user.is_authenticated() or request.user.role_type == 2:
            return HttpResponseRedirect('/app/login/')
        return view(request, *args, **kwargs)

    return temp_view


# 是否必须教练登陆
def coach_login_required(view):
    def temp_view(request, *args, **kwargs):
        if not request.user.is_authenticated() or request.user.role_type == 1:
            return HttpResponseRedirect('/app/login/')
        return view(request, *args, **kwargs)

    return temp_view