#!/usr/bin/env python
# -*- coding: utf-8 -*-
# created by yangxiaodong1214@126.com on 2015/4/20.
import datetime
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse_lazy
from django.shortcuts import render, HttpResponseRedirect
from app.models import *
from django.db.models import Count
from ..forms.admin import *


def login(request):
    '''用户登录view'''
    if request.user.is_authenticated():
        return HttpResponseRedirect('/admin/index')

    if request.method == 'GET' and request.GET.has_key('next'):
        next = request.GET['next']
    else:
        next = '/admin/index'
    if request.method == "POST":
        form = LoginUserForm(request, data=request.POST)
        if form.is_valid():
            auth.login(request, form.get_user())
            return HttpResponseRedirect(request.POST['next'])
    else:
        form = LoginUserForm(request)

    kwargs = {
        'request': request,
        'form': form,
        'next': next,
    }

    return render(request, 'admin/login.html', kwargs)


@login_required(login_url=reverse_lazy('login_url'))
def logout(request):
    auth.logout(request)
    return HttpResponseRedirect(reverse_lazy('login_url'), {"next": ""})


@login_required(login_url=reverse_lazy('login_url'))
def change_password(request):
    if request.method == 'POST':
        form = ChangePasswordForm(user=request.user, data=request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse_lazy('login_url'))
    else:
        form = ChangePasswordForm(user=request.user)

    kwvars = {
        'form': form,
        'request': request,
    }

    return render(request, 'admin/changepwd.html', kwvars)

@login_required(login_url=reverse_lazy('login_url'))
def index(request):
    today_min = datetime.datetime.combine(datetime.date.today(), datetime.time.min)
    today_max = datetime.datetime.combine(datetime.date.today(), datetime.time.max)

    today_reserve = DriveReserve.objects.filter(create_time__range=(today_min, today_max)).annotate(
        pcount=Count('user'))
    audit = {}
    # 今日预约总人数
    audit["all_reserve_count"] = today_reserve.count()
    # 已经审核人数
    audit["check_reserve_count"] = today_reserve.filter(audit_status="1").count()
    # 未审核人数
    audit["uncheck_reserve_count"] = today_reserve.filter(audit_status="0").count()
    # 科目二学车人数
    audit["subject_two_reserve_count"] = today_reserve.filter(user__exam_stage="2").count()
    # 科目三学车人数
    audit["subject_three_reserve_count"] = today_reserve.filter(user__exam_stage="3").count()

    status = {}
    # 今天学车人数
    status["today_drive_count"] = today_reserve.count()
    # 实际学车人数
    status["today_arrive_drive_count"] = today_reserve.filter(sign_status="1").count()
    # 未学车人数
    status["today_not_arrive_drive_count"] = today_reserve.filter(sign_status="-1").count()

    number = {}
    all_user = User.objects.filter(role_type=1)
    today_user = all_user.filter(create_time__range=(today_min, today_max))
    # 今天新增学员
    number["today_add_user_count"] = today_user.count()
    #总学员人数
    number["all_user_count"] = all_user.count()
    #科目一人数
    number["stage_one_user_count"] = all_user.filter(exam_stage="1").count()
    #科目二人数
    number["stage_two_user_count"] = all_user.filter(exam_stage="2").count()
    #科目三人数
    number["stage_three_user_count"] = all_user.filter(exam_stage="3").count()
    #科目四人数
    number["stage_four_user_count"] = all_user.filter(exam_stage="4").count()

    kwargs = {
        'audit': audit,
        'status': status,
        'number': number
    }
    return render(request, 'admin/home.html', kwargs)
