#!/usr/bin/env python
# -*- coding: utf-8 -*-

from math import ceil
import datetime

from django.shortcuts import render_to_response
from django.shortcuts import render
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django.db.models import Q
from django.db.models import F

from app.decorators import *
from app.forms import *


# @front_login_required
def login(request):
    '''用户登录'''

    if request.user.is_authenticated():
        if request.user.role_type == 1:
            return HttpResponseRedirect('/app/student_profile/')
        elif request.user.role_type == 2:
            return HttpResponseRedirect('/app/coach_profile/')

    context = {}
    if request.method == 'POST':
        form = LoginUserForm(request, request.POST)
        if form.is_valid():
            user = form.get_user()
            auth.login(request, user)
            if request.user.role_type == 1:
                return HttpResponseRedirect('/app/student_profile/')
            elif request.user.role_type == 2:
                return HttpResponseRedirect('/app/coach_profile/')
        context['form'] = form
    else:
        form = LoginUserForm()
        context['form'] = form
    return render(request, 'app/login.html', context)


# 注销登录
def logout(request):
    auth.logout(request)
    return HttpResponseRedirect('/app/login/')


# 学员首页
@student_login_required
def student_profile(request):
    context = {}
    config_model = Config.objects.get()
    user_model = User.objects.get(pk=request.user.id)
    # 黑名单
    if user_model.is_blacklist and config_model.is_open_blacklist:
        context['is_blacklist'] = True

    context['user'] = request.user
    # 消息个数
    context['message_count'] = user_model.smssendlog_set.filter(is_read=False).count()
    # 预约个数（待签|待审核）
    reserve_model = user_model.drivereserve_set
    context['reserve_count'] = reserve_model.filter(sign_status__gte=0, audit_status__gte=0).count()
    context['exam_list'] = ExamReserve.objects.filter(user=user_model.id).order_by("-create_time")

    context['disable_reverse'] = False
    now_time = datetime.datetime.now()
    the_hour = datetime.time(now_time.hour, now_time.minute, now_time.second)
    close_start_time = config_model.close_start_time
    close_end_time = config_model.close_end_time

    if close_start_time > close_end_time:
        temp_time = close_start_time
        close_start_time = close_end_time
        close_end_time = temp_time

    if the_hour >= close_start_time and the_hour <= close_end_time:
        context['disable_reverse'] = False
    else:
        context['disable_reverse'] = True

    context['disable_start_time'] = close_start_time
    context['disable_end_time'] = close_end_time

    return render_to_response('app/student_index.html', context)


# 学员首页数据
@ajax_request
def load_reserver_data_student(request):
    user = request.user
    page = int(request.GET.get("page", 1))
    reserve_list = DriveReserve.objects.filter(user_id=user.id).order_by('-train_date')
    paginator = Paginator(reserve_list, 5)
    try:
        reserve_list = paginator.page(page)
    except(EmptyPage, InvalidPage):
        reserve_list = None
    return render_to_response('app/load_reserver_data_student.html', {'reserve_list': reserve_list})


# 教练首页
@coach_login_required
def coach_profile(request):
    context = {}
    context['user'] = request.user
    user_model = User.objects.get(pk=request.user.id)
    # 消息个数
    context['message_count'] = user_model.smssendlog_set.filter(is_read=False).count()

    return render_to_response('app/coach_index.html', context)


# 教练首页数据
@ajax_request
def load_reserver_data_coach(request):
    # 页数
    page = int(request.GET.get("page", 1))
    user_id = request.user.id

    today = datetime.date.today()
    tomorrow = today + datetime.timedelta(days=1)

    # 要用到的数据
    temp_data = {}
    reserver_model = DriveReserve.objects.all().filter(coach_id=user_id, audit_status=1, train_date__lte=tomorrow)

    data_dict = reserver_model.distinct().values('train_date').order_by('-train_date')

    # 计算分页
    per_page = 5
    max_len = len(data_dict)
    max_len_float = float(max_len)
    pages = int(ceil(max_len_float / per_page))
    if page > pages:
        return render_to_response('app/load_reserver_data_coach.html', {'list_data': temp_data})
    end_offset = per_page * page
    if end_offset >= max_len:
        end_offset = max_len
    offset = (page - 1) * per_page
    iteration_data = data_dict[offset: end_offset]

    # 组装教练数据
    index = 0
    for item in iteration_data:
        the_day = item['train_date'].day
        temp_data[index] = {}
        temp_data[index]['train_date'] = item['train_date']
        temp_data[index]['today'] = today
        temp_data[index]['tomorrow'] = tomorrow
        temp_data[index]['user_reservers'] = reserver_model.filter(train_date__day=the_day)
        index = index + 1

    return render_to_response('app/load_reserver_data_coach.html', {'list_data': temp_data})


# 学员反馈
@student_login_required
def feedback(request):
    context = {}
    if request.method == 'POST':
        form = FeedbackForm(request.POST)
        if form.is_valid():
            cdata = form.cleaned_data
            model = UserFeedback.objects.create(
                user_id=request.user.id,
                mobile=cdata['mobile'],
                description=cdata['description'],
            )
            model.save()
            messages.success(request, u'投述信息已提交！')
        context['form'] = form
    else:
        form = FeedbackForm(initial={"mobile": request.user.mobile})
        context['form'] = form
    return render(request, 'app/feedback.html', context)


# 消息中心
@login_required
def message_list(request):
    msg_list = SMSSendLog.objects.filter(user_id=request.user.id).order_by('-send_time')
    return render_to_response('app/message_list.html', {'msg_list': msg_list})


# 学员预约
@student_login_required
def reserver(request):
    context = {}

    config_model = Config.objects.get()
    now_time = datetime.datetime.now()

    the_hour = datetime.time(now_time.hour, now_time.minute, now_time.second)
    close_start_time = config_model.close_start_time
    close_end_time = config_model.close_end_time
    if close_start_time > close_end_time:
        temp_time = close_start_time
        close_start_time = close_end_time
        close_end_time = temp_time

    if the_hour < close_start_time or the_hour > close_end_time:
        return HttpResponseRedirect('/app/student_profile/')

    # 学员资料
    user_id = request.user.id
    user_model = User.objects.get(pk=user_id)
    exam_stage = user_model.exam_stage

    # 只有科目2，3才能约车
    if exam_stage < 2 or exam_stage > 3:
        return HttpResponseRedirect('/app/student_profile/')

    # 黑名单
    if user_model.is_blacklist and config_model.is_open_blacklist:
        return HttpResponseRedirect('/app/student_profile/')

    if exam_stage == 1:
        return HttpResponseRedirect('/app/student_profile/')

    return render_to_response('app/reserver2.html', context)


# 学员预约数据
@ajax_request
def load_reserver_data(request):
    context = {}

    # 页数
    today = datetime.datetime.today()
    page = int(request.GET.get('page', 1))

    # 结果数据
    result_data = {}

    # 学员资料
    user = request.user
    user_model = User.objects.get(pk=user.id)
    exam_stage = user_model.exam_stage

    # 时间次数
    available_count = user_model.train_frequency
    day_available_count = available_count.day_reserve_count
    weekend_available_count = available_count.mouth_weekend_reserve_count
    week_available_count = available_count.week_reserve_count

    # 学员对应车
    coach_car_model = user_model.coach_car

    # 提前可预约天数
    per_page = 7
    today_date = today.date()
    advance_day = Config.objects.get().reserve_overday
    now_time = datetime.datetime.now()
    max_date = today_date + datetime.timedelta(days=advance_day)
    # 总条数
    days_obj = max_date - today_date
    days = float(days_obj.days)
    pages = int(ceil(days / per_page))
    page_mod = int(days % per_page)

    # 超过总分页数？
    if page > pages:
        page = pages
    the_day = today_date + datetime.timedelta(days=(page - 1) * per_page)
    offset_date = today_date + datetime.timedelta(days=page * per_page)

    # 最后一页不够
    if offset_date > max_date:
        per_page = page_mod

    # 预约天数不够显示一页？
    if int(days) < per_page:
        per_page = int(days)

    # 学员等级
    user_level = user_model.category
    level_weekdays = user_level.training_weekdays

    # 缓存数据表
    reverse_model = DriveReserve.objects.all()
    disable_datetime_model = DisabledDateTime.objects.filter(coach_car_id=int(coach_car_model.id))
    train_time_span_model = TrainTimeSpan.objects.filter(exam_stage=exam_stage).order_by('start_time')

    stage_two_time = coach_car_model.stage_two_train_time
    stage_three_time = coach_car_model.stage_three_train_time

    stage_two = map(int, eval(stage_two_time))
    stage_three = map(int, eval(stage_three_time))

    # 只要科目2，3的时间段
    if exam_stage == 2:
        train_time_spans = train_time_span_model.filter(pk__in=stage_two).order_by('start_time')
    elif exam_stage == 3:
        train_time_spans = train_time_span_model.filter(pk__in=stage_three).order_by('start_time')
    else:
        context['reserver_list'] = None
        return render_to_response('app/load_reserver_data.html', context)

    # 组装数据， 拼出要显示数据
    for i in range(0, per_page):

        # 结果状态
        reserver_status = True
        # 状态说明
        status_msg = None

        # 当天日期
        each_day = the_day + datetime.timedelta(days=i)
        week_day = each_day.weekday()
        # 当周周一
        week_monday = each_day + datetime.timedelta(days=(0 - week_day))
        # 当周周五
        week_friday = each_day + datetime.timedelta(days=(6 - week_day))

        result_data[i] = {}
        result_data[i]['each_day'] = each_day

        # 等级判断
        if str(week_day) not in level_weekdays:
            reserver_status = False
            status_msg = u'你所属的会员等级没权限预约'

        if week_day in [5, 6]:
            # 当月的周末已用次数
            weekend_count = reverse_model.filter(
                Q(train_date__year=each_day.year, train_date__month=each_day.month,
                 audit_status__gte=0, user=user_model.id, is_admin_reserve=False)
                & (Q(train_date__week_day=5) | Q(train_date__week_day=6))).count()
            if weekend_count >= weekend_available_count:
                reserver_status = False
                status_msg = u'这个月这周周末的预约次数已用完'
        else:
            # 每个月的每周工作日次数
            week_count = reverse_model.filter(user=user_model.id,
                                              audit_status__gte=0,
                                              train_date__year=each_day.year,
                                              train_date__month=each_day.month,
                                              train_date__gte=week_monday,
                                              train_date__lte=week_friday,
                                              is_admin_reserve=False).count()
            if week_count >= week_available_count:
                reserver_status = False
                status_msg = u'这个月的这周内的预约次数已用完'

        # 当天
        day_count = reverse_model.filter(user=user_model.id,
                                         train_date=each_day,
                                         audit_status__gte=0,
                                         is_admin_reserve=False).count()
        if day_count >= day_available_count:
            reserver_status = False
            status_msg = u'今天的预约次数已用完'

        # 每天时间段
        day_times = []
        # 遍历所有时间有时间段
        for item in train_time_spans:
            inner_status = True
            inner_status_msg = None

            if each_day <= max_date:
                limit_condition = Q(is_admin_reserve=False)
            else:
                limit_condition = Q()
            is_my_reversed = reverse_model.filter(Q(coach_car_id=int(coach_car_model.id), train_time_span_id=item.id,
                                                    audit_status__gte=0, user=user_model.id,
                                                    exam_stage=exam_stage,
                                                    train_date=each_day) & limit_condition).exists()
            if is_my_reversed:
                inner_status = False
                inner_status_msg = u'你已经预约了本时间段，不可重复预约'
            else:
                is_other_reversed = reverse_model.filter(
                    Q(coach_car_id=int(coach_car_model.id), train_time_span_id=item.id,
                      audit_status__gte=0, exam_stage=exam_stage,
                      train_date=each_day) & limit_condition).exists()
                if is_other_reversed:
                    inner_status = False
                    inner_status_msg = u'本时间段已被预约，请预约其他时间段'

            # 教练车在此时间可用吗？
            the_start_time = datetime.datetime.combine(each_day, item.start_time)
            the_end_time = datetime.datetime.combine(each_day, item.end_time)

            if the_start_time < now_time:
                inner_status = False
                inner_status_msg = u'只能预约当前时间之后的时间段'

            # 教练车禁用
            is_disabled_time = disable_datetime_model.filter(
                Q(begin_datetime__gt=the_start_time, begin_datetime__lt=the_end_time) |
                Q(begin_datetime__lt=the_start_time, end_datetime__gt=the_end_time) |
                Q(end_datetime__gt=the_start_time, end_datetime__lt=the_end_time)).exists()

            if is_disabled_time is True:
                inner_status = False
                inner_status_msg = u'教练车在此时间段不可用'

            final_status = reserver_status
            if inner_status is False:
                final_status = False

            final_status_msg = status_msg
            if inner_status_msg:
                final_status_msg = inner_status_msg

            item_obj = {}
            item_obj['id'] = item.id
            item_obj['status'] = final_status
            item_obj['status_msg'] = final_status_msg
            item_obj['start_time'] = item.start_time
            item_obj['end_time'] = item.end_time
            item_obj['name'] = item.name
            item_obj['user'] = user
            day_times.append(item_obj)

        result_data[i]['time_frame'] = day_times

    context['reserver_list'] = result_data
    context['current_page'] = page
    context['total_page'] = pages
    return render_to_response('app/load_reserver_data.html', context)


# 忘记密码
def forget_password(request):
    return render(request, 'app/forget_password.html')


# 申请考试
@student_login_required
def exam(request):
    context = {}
    exam_stage = (
        ('1', u'科目一'),
        ('2', u'科目二'),
        ('3', u'科目三'),
        ('4', u'科目四'),
    )
    stage = request.user.exam_stage
    if stage == 2:
        aviable_stage = (
            ('2', u'科目二'),
        )
    else:
        aviable_stage = exam_stage[int(stage) - 1:]

    context['aviable_stage'] = aviable_stage
    if request.method == 'POST':

        post_stage = request.POST.get('exam_stage')
        user = User.objects.get(pk=int(request.user.id))
        is_verify = ExamReserve.objects.filter(exam_stage=post_stage, user=user, audit_status=0).exists()
        if is_verify:
            messages.success(request, '你已经申请过此科目的考试，请耐心等待审核！')
            form = ExamForm()
            context['form'] = form
            return render(request, 'app/exam.html', context)
        else:
            form = ExamForm(request.POST)
            if form.is_valid():
                cdata = form.cleaned_data
                model = ExamReserve.objects.create(
                    user_id=request.user.id,
                    exam_stage=cdata['exam_stage'],
                    remarks=cdata['remarks'],
                    audit_status=0,
                )
                model.save()
                messages.success(request, '申请信息已提交，请等待管理员审核！')
            context['form'] = form
    else:
        form = ExamForm()
        context['form'] = form
    return render(request, 'app/exam.html', context)