#!/usr/bin/env python
# -*- coding: utf-8 -*-
# created by yangxiaodong1214@126.com on 2015/4/13.

import datetime
from django.core.urlresolvers import reverse_lazy
from django.shortcuts import HttpResponse, HttpResponseRedirect
from django.views.generic.detail import DetailView
from ..common import SMSFactory, adduserlog, SMSLogic, JsonResponse
from .generic import *
from ..forms.user import *
from ..filter import *


# ============套餐类别===========

class CategoryList(FilterView):
    template_name = 'admin/user/categorylist.html'
    queryset = ClassCategory.objects.all()
    context_object_name = 'category_list'
    filterset_class = CategoryFilter


class CategoryCreate(MyCreateView):
    template_name = 'admin/user/categoryadd.html'
    form_class = CategoryCreateForm
    model = ClassCategory
    success_url = reverse_lazy('list_category_url')


class CategoryUpdate(MyUpdateView):
    template_name = 'admin/user/categorymodify.html'
    form_class = CategoryCreateForm
    model = ClassCategory
    success_url = reverse_lazy('list_category_url')


class CategoryDelete(MyDeleteView):
    model = ClassCategory


# =========用户反馈==========

class FeedbackList(FilterView):
    template_name = 'admin/user/feedbacklist.html'
    queryset = UserFeedback.objects.all()
    context_object_name = 'feedback_list'
    filterset_class = FeedBackFilter


class FeedbackDelete(MyDeleteView):
    model = UserFeedback


class FeedbackView(MyUpdateView):
    template_name = 'admin/user/feedbackview.html'
    model = UserFeedback

    def post(self, request, *args, **kwargs):
        remark = request.POST.get("remarks")
        model = self.get_object()
        model.remarks = remark
        model.audit_status = 1
        model.audit_time = datetime.datetime.now()
        model.save()
        return HttpResponseRedirect(reverse_lazy("list_feedback_url"))


# =========学员等级（练车频率）======

class FrequencyList(MyFilterView):
    template_name = 'admin/user/frequencylist.html'
    queryset = TrainFrequency.objects.all()
    context_object_name = 'frequency_list'
    filterset_class = FrequencyFilter


class FrequencyCreate(MyCreateView):
    template_name = 'admin/user/frequencyadd.html'
    form_class = FrequencyCreateForm
    model = TrainFrequency
    success_url = reverse_lazy('list_frequency_url')


class FrequencyUpdate(MyUpdateView):
    template_name = 'admin/user/frequencymodify.html'
    form_class = FrequencyCreateForm
    model = TrainFrequency
    success_url = reverse_lazy('list_frequency_url')


class FrequencyDelete(MyDeleteView):
    model = TrainFrequency


# ==========学员信息===========

class UserList(MyFilterView):
    ajax_template_name = 'admin/user/_partialuserlist.html'
    template_name = 'admin/user/userlist.html'
    queryset = User.objects.filter(is_superuser=False, role_type=1).order_by('-create_time')
    context_object_name = 'user_list'
    filterset_class = UserFilter


def get_user_list(request):
    if not request.is_ajax():
        return HttpResponse(u'异常请求')
    name = request.GET.get("name")
    mobile = request.GET.get("mobile")
    user_list = User.objects.filter(is_superuser=False, role_type=1,
                                    name__icontains=name, mobile__icontains=mobile).order_by('-create_time')
    dic_list = []
    for item in user_list:
        dic = {}
        dic["id"] = item.id
        dic["name"] = item.name
        dic["mobile"] = item.mobile
        dic["id_card"] = item.id_card
        dic["reserve_count"] = item.get_reserve_count
        dic_list.append(dic)
    return JsonResponse({"result": "ok", "user_list": dic_list})


class UserCreate(MyCreateView):
    template_name = 'admin/user/useradd.html'
    form_class = UserCreteForm
    model = User
    success_url = reverse_lazy('list_user_url')

    def form_valid(self, form):
        user = form.save(commit=False)
        pwd = form.cleaned_data['id_card'][-6:]
        user.set_password(pwd)
        user.exam_stage_status = 1
        user.save()
        self.object = user
        if user.exam_stage == 1:
            SMSLogic(user).send_register_sms()
        adduserlog(user, u"添加学员", u"录入学员资料")
        return HttpResponseRedirect(self.get_success_url())


class UserUpdate(MyUpdateView):
    template_name = 'admin/user/usermodify.html'
    form_class = UserModifyForm
    model = User
    success_url = reverse_lazy('list_user_url')

    def form_valid(self, form):
        old_user = self.get_object()
        user = form.save(commit=False)
        if old_user.password != user.password:
            user.set_password(user.password)
        user.save()

        description = ""
        if old_user.name != user.name:
            description += u"姓名:(" + old_user.name + "->" + user.name + ");"
        if old_user.id_card != user.id_card:
            description += u"身份证号:(" + old_user.id_card + "->" + user.id_card + ");"
        if old_user.mobile != user.mobile:
            description += u"手机号:(" + old_user.mobile + "->" + user.mobile + ");"
        if old_user.age != user.age:
            description += u"年龄:(" + old_user.age + "->" + user.age + ");"
        if old_user.train_frequency != user.train_frequency:
            description += u"学员等级:(" + str(old_user.train_frequency) + "->" + str(user.train_frequency) + ");"
        if old_user.exam_stage != user.exam_stage:
            description += u"学员等级:(" + str(old_user.train_frequency) + "->" + str(user.train_frequency) + ");"
        if old_user.category != user.category:
            description += u"教学模式:(" + str(old_user.category) + "->" + str(user.category) + ");"
        if old_user.coach_car != user.coach_car:
            description += u"教练车:(" + str(old_user.coach_car) + "->" + str(user.coach_car) + ");"

        adduserlog(old_user, u"修改学员", description)
        return HttpResponseRedirect(self.get_success_url())


def get_exam_reserve(userid, exam_stage):
    return ExamReserve.objects.filter(
        user=userid, exam_stage=exam_stage).order_by('-create_time')


def get_drive_reserve(userid, exam_stage):
    return DriveReserve.objects.filter(
        user=userid, exam_stage=exam_stage).order_by('-train_date')


class UserView(DetailView):
    model = User
    template_name = 'admin/user/userview.html'

    def get_context_data(self, **kwargs):
        context = super(UserView, self).get_context_data(**kwargs)
        user = self.get_object()
        three_drive_reserve_log = get_drive_reserve(user.id, 3)
        two_drive_reserve_log = get_drive_reserve(user.id, 2)
        one_drive_reserve_log = get_drive_reserve(user.id, 1)
        three_exam_reserve_log = get_exam_reserve(user.id, 3)
        two_exam_reserve_log = get_exam_reserve(user.id, 2)
        one_exam_reserve_log = get_exam_reserve(user.id, 1)
        context['user_log_object'] = user.userlog_set
        context['three_drive_reserve_log'] = three_drive_reserve_log
        context['two_drive_reserve_log'] = two_drive_reserve_log
        context['one_drive_reserve_log'] = one_drive_reserve_log
        context['three_exam_reserve_log'] = three_exam_reserve_log
        context['two_exam_reserve_log'] = two_exam_reserve_log
        context['one_exam_reserve_log'] = one_exam_reserve_log
        context['exam_stage_status'] = EXAM_STAGE_STATUS
        return context


class UserDelete(MyDeleteView):
    model = User


def change_user_stage_status(request):
    if request.method == "POST":
        if request.is_ajax():
            user_id = int(request.POST.get("userid"))
            status = int(request.POST.get("status"))
            user = User.objects.get(pk=user_id)
            user_stage = user.exam_stage_status

            if user_stage > status and user_stage != 4:
                return JsonResponse({"result": u"状态不可逆"})

            user.exam_stage_status = status
            exam_stage = user.exam_stage
            # ((1, '不可约考'), (2, '约考成功'), (3, '考试通过'), (4, '考试未通过'))
            sms = SMSFactory(user)
            if status == 1:
                return JsonResponse({"result": u"不能切换到不可预约"})
            elif status == 2:
                sms.send_reserve()
                adduserlog(user, u"修改科目状态", u"学员科目状态被修改为：约考成功")
            elif status == 3:
                sms.send_pass()
                adduserlog(user, u"修改科目状态", u"学员科目状态被修改为：考试通过")
                # 如果是通过
                if exam_stage <= 4:
                    user.exam_stage = exam_stage + 1
                    user.exam_stage_status = 1
            else:
                sms.send_not_pass()
                adduserlog(user, u"修改科目状态", u"学员科目状态被修改为：考试未通过")
            user.save()
            return JsonResponse({"result": "Ok"})
        else:
            return JsonResponse({"result": "Error"})
    else:
        raise Exception(u'异常请求')


# =======学员黑名单============

class BlackList(FilterView):
    template_name = 'admin/user/blacklist.html'
    queryset = User.objects.filter(is_superuser=False, role_type=1, is_blacklist=True)
    context_object_name = 'black_list'
    filterset_class = BlackFilter


class BlackDelete(MyDeleteView):
    success_url = reverse_lazy('list_black_url')
    model = User

    def delete(self, request, *args, **kwargs):
        user = self.get_object()
        user.is_blacklist = False
        user.current_not_arrival_count = 0
        user.save()



