#!/usr/bin/env python
# -*- coding: utf-8 -*-
from django.shortcuts import render
from ..common import JsonResponse
from django.db.models import ProtectedError
from django_filters.views import FilterView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.utils.decorators import method_decorator
from django.core.urlresolvers import reverse_lazy
from django.contrib.auth.decorators import login_required


class MyFilterView(FilterView):
    is_ajax = False
    is_loadpage = True

    @method_decorator(login_required(login_url=reverse_lazy("login_url")))
    def dispatch(self, *args, **kwargs):
        return super(MyFilterView, self).dispatch(*args, **kwargs)

class MyCreateView(CreateView):
    def form_valid(self, form):
        return super(MyCreateView, self).form_valid(form)

    @method_decorator(login_required(login_url=reverse_lazy("login_url")))
    def dispatch(self, request, *args, **kwargs):
        return super(MyCreateView, self).dispatch(request, *args, **kwargs)


class MyUpdateView(UpdateView):
    def form_valid(self, form):
        return super(MyUpdateView, self).form_valid(form)

    @method_decorator(login_required(login_url=reverse_lazy("login_url")))
    def dispatch(self, request, *args, **kwargs):
        return super(MyUpdateView, self).dispatch(request, *args, **kwargs)


class MyDeleteView(DeleteView):
    success_url = '/'

    @method_decorator(login_required(login_url=reverse_lazy("login_url")))
    def dispatch(self, *args, **kwargs):
        # maybe do some checks here for permissions ...
        response = None
        response_data = {"result": "ok", "message": u"删除成功！"}
        try:
            response = super(MyDeleteView, self).dispatch(*args, **kwargs)
        except ProtectedError as e:
            msg = u"下列对象还在使用该信息，不能删除.\r\n"
            # 级联删除
            for index, item in enumerate(e.protected_objects, start=1):
                msg += str(item) + ", "
                if index % 4 == 0:
                    msg += '\r\n'
                if index > 11:
                    msg += '....'
                    break
            response_data = {"result": "fail", "message": msg}
        if self.request.is_ajax():
            return JsonResponse(response_data)
        else:
            return response


