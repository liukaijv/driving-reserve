#!/usr/bin/env python
# -*- coding: utf-8 -*-

import datetime

from django.http import HttpResponse
from django.views.decorators.http import require_POST
from django.forms.formsets import BaseFormSet
from django.core import serializers
from django.db.models import Q
from django.db.models import F

from app.utils import *
from app.forms import *
from app.decorators import *
from admin.common import SMSLogic


# ajax 验证
def ajax_validate(request, *args, **kwargs):
    form_class = kwargs.pop('form_class')
    defaults = {
        'data': request.POST
    }
    extra_args_func = kwargs.pop('callback', lambda request, *args, **kwargs: {})
    kwargs = extra_args_func(request, *args, **kwargs)
    defaults.update(kwargs)
    form = form_class(**defaults)
    if form.is_valid():
        data = {
            'valid': True,
        }
    else:
        # if we're dealing with a FormSet then walk over .forms to populate errors and formfields
        if isinstance(form, BaseFormSet):
            errors = {}
            formfields = {}
            for f in form.forms:
                for field in f.fields.keys():
                    formfields[f.add_prefix(field)] = f[field]
                for field, error in f.errors.iteritems():
                    errors[f.add_prefix(field)] = error
            if form.non_form_errors():
                errors['__all__'] = form.non_form_errors()
        else:
            errors = form.errors
            formfields = dict([(fieldname, form[fieldname]) for fieldname in form.fields.keys()])

        # if fields have been specified then restrict the error list
        if request.POST.getlist('fields'):
            fields = request.POST.getlist('fields') + ['__all__']
            errors = dict([(key, val) for key, val in errors.iteritems() if key in fields])

        final_errors = {}
        for key, val in errors.iteritems():
            if '__all__' in key:
                final_errors[key] = val
            elif not isinstance(formfields[key].field, forms.FileField):
                html_id = formfields[key].field.widget.attrs.get('id') or formfields[key].auto_id
                html_id = formfields[key].field.widget.id_for_label(html_id)
                final_errors[html_id] = val
        data = {
            'valid': False or not final_errors,
            'errors': final_errors,
        }
    json_serializer = LazyEncoder()
    return HttpResponse(json_serializer.encode(data), mimetype='application/json')


validate = require_POST(ajax_validate)

# 用户登陆
@ajax_request
def do_login(request):
    form = LoginUserForm(request, data=request.POST)
    if form.is_valid():
        # if user.is_active:
        auth.login(request, form.get_user())
        user = request.user
        if user.role_type == 1:
            return ajax_ok(next='/app/student_profile/')
        elif user.role_type == 2:
            return ajax_ok(next='/app/coach_profile/')
    return ajax_fail()


# 生成预约单
@ajax_request
def order_action(request):
    form = LoginUserForm(request.POST)
    if form.is_valid():
        cdata = form.cleaned_data
        # 预约单
        drive_model = DriveReserve.objects.create(
            user=request.user.id,
            train_time_span=cdata['train_time_span'],
            remarks=cdata['remarks'],
        )
        drive_model.save()
        # todo 更新user数据
        # todo 写入日志
        return ajax_ok({})


# 更改预约单状态
@ajax_request
def change_sign_status(request):
    sign_status = int(request.POST.get('sign_status', 0))
    obj_id = int(request.POST.get('id'))
    if sign_status not in [-1, 1]:
        return ajax_fail(msg=u'参数不正确', sign_status=0)
    model = DriveReserve.objects.get(pk=obj_id)
    if model.sign_status != 0:
        return ajax_fail(msg=u'你已经进行过签到了', sign_status=0)
    DriveReserve.objects.filter(pk=obj_id).update(sign_status=sign_status)

    user_model = User.objects.filter(pk=model.user.id)
    config_model = Config.objects.get()
    blacklist_breakpoint = config_model.blacklist_break

    if sign_status == 1:
        user_model.update(arrival_count=F('arrival_count') + 1)
        return ajax_ok(msg=u'状态已标记为已到', sign_status=1)
    elif sign_status == -1:
        user_model.update(not_arrival_count=F('not_arrival_count') + 1)
        not_arrival_count = User.objects.get(pk=model.user.id).not_arrival_count
        if not_arrival_count == blacklist_breakpoint:
            SMSLogic(user_model).send_black_list_add()
        if not_arrival_count >= blacklist_breakpoint:
            user_model.update(is_blacklist=True)
        else:
            user_model.update(is_blacklist=False)
        return ajax_ok(msg=u'状态已标记为未到', sign_status=-1)
    else:
        return ajax_fail(msg=u'操作失败', sign_status=0)


# 预约条件
@ajax_request
def confirm_order_condition(request):
    train_time_span_id = request.POST.get('train_time_span_id', None)
    train_date = request.POST.get('train_date', None)

    if not train_time_span_id:
        return ajax_fail(msg=u'请先选择预约时间段')
    if not train_date:
        return ajax_fail(msg=u'选择的日期有错误')
    time_span_id = int(train_time_span_id)

    # 学员资料
    user_id = request.user.id
    user_model = User.objects.get(pk=user_id)
    coach_car_model = user_model.coach_car
    exam_stage = user_model.exam_stage
    train_time_span = TrainTimeSpan.objects.get(pk=time_span_id, exam_stage=exam_stage)
    training_place = coach_car_model.training_place
    coach = User.objects.get(role_type=2, coach_car_id=coach_car_model.id)
    if exam_stage == 1:
        return ajax_fail(msg=u'您在科目一阶段还没资格约车哦')

    # 黑名单
    config_model = Config.objects.get()
    if user_model.is_blacklist and config_model.is_open_blacklist:
        return ajax_fail(msg=u'你在黑名单中，请联系管理员')

    # 当前时间
    now_time = datetime.datetime.now()
    start_time = train_time_span.start_time
    end_time = train_time_span.end_time
    the_day = datetime.datetime.strptime(train_date, "%Y-%m-%d")
    the_start_time = the_day + datetime.timedelta(hours=start_time.hour)

    start_time_hour = str(train_time_span.id)

    if exam_stage == 2:
        stage_two_time = coach_car_model.stage_two_train_time
        if start_time_hour not in stage_two_time:
            return ajax_fail(msg=u'科目二不能预约此时间段')
    if exam_stage == 3:
        stage_three_time = coach_car_model.stage_three_train_time
        if start_time_hour not in stage_three_time:
            return ajax_fail(msg=u'科目三不能预约此时间段')

    # 时间点过期了没？
    if the_start_time < now_time:
        return ajax_fail(msg=u'只能预约当前时间之后的时间段')

    the_end_time = the_day + datetime.timedelta(hours=end_time.hour)
    week_day = the_day.weekday()

    # 当周周一
    week_monday = the_day + datetime.timedelta(days=(0 - week_day))
    # 当周周日
    week_friday = the_day + datetime.timedelta(days=(7 - week_day))

    # 学员等级
    user_level = user_model.category
    if str(week_day) not in user_level.training_weekdays:
        return ajax_fail(msg=u'你所属的会员等级没权限预约')

    # 预约表
    drive_reserve_model = DriveReserve.objects.all()

    # 些时间段约满？
    is_my_reversed = drive_reserve_model.filter(coach_car_id=int(coach_car_model.id), train_time_span_id=time_span_id,
                                                audit_status__gte=0, user=user_model.id,
                                                exam_stage=exam_stage,
                                                train_date=the_day).exists()
    if is_my_reversed:
        return ajax_fail(msg=u'你已经预约了本时间段，不可重复预约')
    else:
        is_other_reversed = drive_reserve_model.filter(train_time_span_id=time_span_id,
                                                       audit_status__gte=0, coach_car_id=int(coach_car_model.id),
                                                       exam_stage=exam_stage,
                                                       train_date=the_day).exists()
        if is_other_reversed:
            return ajax_fail(msg=u'本时间段已被预约，请预约其他时间段')

    # 教练车可用吗？
    disabled_time = DisabledDateTime.objects.filter(
        Q(coach_car_id=int(coach_car_model.id))
        & (Q(begin_datetime__gt=the_start_time, begin_datetime__lt=the_end_time) |
           Q(begin_datetime__lt=the_start_time, end_datetime__gt=the_end_time) |
           Q(end_datetime__gt=the_start_time, end_datetime__lt=the_end_time))) \
        .exists()

    if disabled_time is True:
        return ajax_fail(msg=u'教练车在此时间段不可用')

    # 次数限制
    available_count = user_model.train_frequency
    day_available_count = available_count.day_reserve_count
    weekend_available_count = available_count.mouth_weekend_reserve_count
    week_available_count = available_count.week_reserve_count

    # 套餐判断
    # 当月此阶段的一个周
    # 当月的周末已用次数
    if week_day in [5, 6]:
        weekend_count = drive_reserve_model.filter(
            Q(train_date__year=the_day.year, train_date__month=the_day.month, user=user_model.id, audit_status__gte=0,
              is_admin_reserve=False)
            & (Q(train_date__week_day=5) | Q(train_date__week_day=6))).count()
        if weekend_count >= weekend_available_count:
            return ajax_fail(msg=u'这周周末的预约次数已用完')
    else:
        # 每个月的每周工作日次数
        week_count = drive_reserve_model.filter(user=user_model.id,
                                                audit_status__gte=0,
                                                train_date__year=the_day.year,
                                                train_date__month=the_day.month,
                                                train_date__gte=week_monday,
                                                train_date__lte=week_friday).count()
        if week_count >= week_available_count:
            return ajax_fail(msg=u'这周的预约次数已用完')
    # 当天
    day_count = drive_reserve_model.filter(user=user_model.id,
                                           train_date=the_day,
                                           audit_status__gte=0).count()
    if day_count >= day_available_count:
        return ajax_fail(msg=u'今天预约次数已用完')

    try:
        model = DriveReserve.objects.create(
            user_id=request.user.id,

            coach_id=coach.id,
            coach_name=coach.name,

            coach_car_id=coach_car_model.id,
            coach_car_license=coach_car_model.license,

            train_time_span_id=train_time_span.id,
            train_time_span_name=train_time_span.name,
            train_time_span_start_time=train_time_span.start_time,
            train_time_span_end_time=train_time_span.end_time,

            training_place_id=training_place.id,
            training_place_name=training_place.place_name,

            train_date=the_day,
            exam_stage=exam_stage
        )
        model.save()
        return ajax_ok(msg=u'预约申请成功，等待后台审核！', next="/app/student_profile/")
    except:
        return ajax_fail(msg=u'数据保存失败！', next="/app/student_profile/")


@ajax_request
def order_view(request):
    order_id = request.POST['id']
    json_data = serializers.serialize("json", DriveReserve.objects.select_related().filter(pk=order_id))
    return ajax_ok(json_data=json_data)


# 投诉
@ajax_request
def do_feedback(request):
    form = FeedbackForm(request.POST)
    if form.is_valid():
        cdata = form.cleaned_data
        try:
            model = UserFeedback.objects.create(
                user_id=request.user.id,
                mobile=cdata['mobile'],
                description=cdata['description'],
            )
            model.save()
            return ajax_ok(msg=u'你的投诉信息已提交！')
        except:
            return ajax_fail(msg=u'出错了')
    return ajax_fail(msg=u'出错了')


# 查看信息
def message_view(request):
    message_id = request.POST['id']
    SMSSendLog.objects.filter(pk=int(message_id)).update(is_read=True)
    json_data = serializers.serialize("json", SMSSendLog.objects.filter(pk=message_id))
    return ajax_ok(json_data=json_data)


# 删除信息
# @ajax_request
def message_delete(request):
    message_id = request.POST['id']
    try:
        SMSSendLog.objects.filter(pk=int(message_id)).delete()
        return ajax_ok(msg=u'信息已删除', next="/app/message_list/")
    except:
        return ajax_fail(msg=u'出错了')


# 申请考试
@ajax_request
def do_exam(request):
    form = ExamForm(request.POST)
    if form.is_valid():
        cdata = form.cleaned_data
        try:
            model = ExamReserve.objects.create(
                user_id=request.user.id,
                exam_stage=cdata['exam_stage'],
                remarks=cdata['remarks'],
                audit_status=0,
            )
            model.save()
            return ajax_ok(msg=u'你的考试申请已提交！')
        except:
            return ajax_fail(msg=u'保存数据出错了！')
    return ajax_fail(msg=u'你的考试申请提交失败！')

