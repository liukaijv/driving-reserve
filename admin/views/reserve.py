#!/usr/bin/env python
# -*- coding: utf-8 -*-

import ast
from django.contrib import messages
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView
from django.contrib import messages
from django.shortcuts import HttpResponseRedirect, render
from ..filter import ExamReserveFilter, DriveReserveFilter
from .generic import *
from ..common import *
from app.utils import ajax_ok, ajax_fail

# ===========练车预约=========

def drive_add(request):
    return render(request, 'admin/reserve/driveadd.html')


def reserve_form(request):
    if request.method == "GET":
        id = request.GET["id"]
        if id:
            user = User.objects.get(pk=id)
            car_id = user.coach_car.id
            coach = User.objects.get(role_type=2, coach_car_id=car_id)
            if user.exam_stage == 1 or user.exam_stage == 2:
                reserve_time = user.coach_car.stage_two_train_time
            else:
                reserve_time = user.coach_car.stage_three_train_time
            reserve_time = ast.literal_eval(reserve_time)
            reserve_time = TrainTimeSpan.objects.filter(pk__in=reserve_time).values_list('id', 'name')
            return render(request, 'admin/reserve/_patialreserve.html',
                          {"user": user,
                           "coach": coach,
                           "reserve_time": reserve_time
                           })
    else:
        user_id = request.POST["userid"]
        reservedate = request.POST["reservedate"]
        trains_time = request.POST.getlist('reservetime[]')
        if request.is_ajax():
            drive_reserve = DriveReserve.objects.filter(user=user_id,
                                                        train_date=reservedate,
                                                        train_time_span_id__in=trains_time)
            result = {"result": ""}
            if drive_reserve.count() == 0:
                result["result"] = "ok"
            else:
                drive_list = drive_reserve.values('train_time_span_name')
                for item in drive_list:
                    result["result"] += str(item['train_time_span_name']) + " "
                result["result"] += u"已经被预约了。"
            return JsonResponse(result)
        else:

            reserve_logic = ReserveLogic()
            for time in trains_time:
                reser = reserve_logic.reserve(user_id, reservedate, time)
                user = User.objects.get(pk=user_id)
                try:
                    SMSLogic(user).send_reserve_sms(reser.id)
                except:
                    pass
            return HttpResponseRedirect(reverse_lazy('list_drive_reserve_url'))


def drive_list(request):
    pass


def drive_check(request):
    if not request.is_ajax():
        return ajax_fail(message=u'异常请求')

    id = request.POST["id"]
    type = request.POST["type"]
    remarks = request.POST["remarks"]

    reserve_logic = ReserveLogic()
    reserve = DriveReserve.objects.get(pk=id)
    sms_logic = SMSLogic(reserve.user)
    try:
        if type == "refuse":
            reserve_logic.refuse_reserve(reserve.id, remarks)
            sms_logic.refuse_reserve_sms(reserve.id)
        if type == "pass":
            reserve_logic.pass_reserve(reserve.id, remarks)
            sms_logic.send_reserve_sms(reserve.id)
        if type == "cancel":
            reserve_logic.cancel_reserve(reserve.id, remarks)
            sms_logic.cancel_reserve_sms(reserve.id)
        return ajax_ok(message=u'操作成功')
    except Exception as e:
        return ajax_fail(message=u'操作失败' + e.message)


def drive_batch_delete(request):
    if not request.is_ajax():
        return ajax_fail(message=u'异常请求')
    ids = request.POST["ids"]
    id_list = ids.split(',')
    for id in id_list:
        if id == u'':
            continue
        drive = DriveReserve.objects.get_or_none(pk=int(id))
        if drive:
            drive.delete()
    return ajax_ok(message=u'操作成功')


def drive_batch_audit(request):
    if not request.is_ajax():
        return HttpResponse('异常请求')
    ids = request.POST["ids"]
    id_list = ids.split(',')
    reserve_logic = ReserveLogic()
    msg = ""
    for id in id_list:
        if id == u'':
            continue
        reserve = DriveReserve.objects.get(pk=id)
        sms_logic = SMSLogic(reserve.user)
        try:
            if reserve.audit_status == 0:
                if not reserve.is_past_due:
                    reserve_logic.pass_reserve(reserve.id, '')
                    sms_logic.send_reserve_sms(reserve.id)
                else:
                    msg += reserve.user.name + "(过期), "
            else:
                msg += reserve.user.name + "(跳过), "
        except Exception as e:
            logger.error(e.message)
    messages.success(request, '操作成功! ' + msg)
    return ajax_ok(message=u'操作成功')


class DriveReserveDelete(MyDeleteView):
    model = DriveReserve


class DriveReserveList(MyFilterView):
    template_name = 'admin/reserve/drivelist.html'
    queryset = DriveReserve.objects.all()
    context_object_name = 'drive_reserve_list'
    filterset_class = DriveReserveFilter


class DriveReserveDetail(DetailView):
    template_name = 'admin/reserve/drivedetails.html'
    context_object_name = 'reserve'
    model = DriveReserve


class DriveReserveNotice(ListView):
    template_name = 'admin/reserve/drivenotice.html'
    model = DriveReserve

    def get_context_data(self, **kwargs):
        context = super(DriveReserveNotice, self).get_context_data(**kwargs)
        data_list = self.model.objects.filter(is_alert=False).order_by('-train_date')[0:10]
        context['data_list'] = data_list
        all_list = self.model.objects.filter(is_alert=False).order_by('-train_date')
        context['all_list'] = all_list
        context['sum_count'] = all_list.count()
        context['verify_count'] = self.model.objects.filter(audit_status=0).count()
        context['exam_count'] = ExamReserve.objects.filter(audit_status=0).count()
        context['msg_count'] = UserFeedback.objects.filter(audit_status=0).count()
        context['black_list_count'] = User.objects.filter(is_blacklist=True, role_type=1).count()
        return context


def drive_toggle_alert(request):
    if not request.is_ajax() and request.POST.get('id'):
        return ajax_fail(message=u'异常请求')
    drive_id = request.POST.get('id')
    DriveReserve.objects.extra(where=['id IN (' + drive_id + ')']).update(is_alert=True)
    return ajax_ok(message=u'修改成功')


# ===========考试预约=========


def exam_check(request):
    if not request.is_ajax():
        return ajax_fail(message=u'异常请求')

    id = request.POST["id"]
    type = request.POST["type"]
    reserve_logic = ExamReserveLogic()
    reserve = ExamReserve.objects.get(pk=id)
    sms_logic = SMSLogic(reserve.user)
    try:
        if type == "refuse":
            reserve_logic.refuse_reserve(reserve.id)
            sms_logic.refuse_exam_reserve_sms(reserve.id)
        if type == "pass":
            reserve_logic.pass_reserve(reserve.id)
            sms_logic.send_exam_reserve_sms(reserve.id)
        return ajax_ok(message=u'操作成功')
    except Exception as e:
        return ajax_fail(message=u'操作失败' + e.message)


class ExamReserveDetail(DetailView):
    template_name = 'admin/reserve/examdetails.html'
    context_object_name = 'exam'
    model = ExamReserve


class ExamReserveList(MyFilterView):
    template_name = 'admin/reserve/examlist.html'
    queryset = ExamReserve.objects.all().order_by('-create_time')
    context_object_name = 'exam_reserve_list'
    filterset_class = ExamReserveFilter


class ExamReserveDelete(MyDeleteView):
    model = ExamReserve


def exam_batch_delete(request):
    if not request.is_ajax():
        return ajax_fail(message='异常请求')
    ids = request.POST["ids"]
    id_list = ids.split(',')
    for id in id_list:
        if id == u'':
            continue
        exam = ExamReserve.objects.get_or_none(pk=int(id))
        if exam:
            exam.delete()
    messages.success(request, '记录删除成功')
    return ajax_ok(message='操作成功')


def exam_batch_audit(request):
    if not request.is_ajax():
        return ajax_fail(message='异常请求')
    ids = request.POST["ids"]
    id_list = ids.split(',')
    reserve_logic = ExamReserveLogic()
    for id in id_list:
        if id == u'':
            continue
        reserve = ExamReserve.objects.get(pk=int(id))
        sms_logic = SMSLogic(reserve.user)
        try:
            if reserve.audit_status == 0:
                reserve_logic.pass_reserve(reserve.id)
                sms_logic.send_exam_reserve_sms(reserve.id)
        except Exception as e:
            logger.error(e.message)
    messages.success(request, '审核成功')
    return ajax_ok(message='操作成功')
