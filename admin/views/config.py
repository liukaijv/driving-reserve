#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
from django.contrib import messages
from ..forms.config import *
from .generic import *
from ..filter import SMSTemplateFilter, SMSLogFilter
from ..smsglobal import SmsBackend
from ..common import SMSLogic
from app.utils import ajax_ok, ajax_fail


reload(sys)
sys.setdefaultencoding("utf-8")

# ===========基础配置============

class ConfigUpdate(MyUpdateView):
    template_name = 'admin/config/basiclist.html'
    form_class = ConfigForm
    model = Config
    context_object_name = 'config'
    success_url = reverse_lazy('list_basic_url')

    def get_object(self, queryset=None):
        return Config.objects.filter()[:1].get()

    def form_valid(self, form):
        messages.success(self.request, "设置保存成功")
        return super(ConfigUpdate, self).form_valid(form)


# ==========短信模板=======

class SMSTemplateList(FilterView):
    template_name = 'admin/config/smstemplatelist.html'
    queryset = SMSTemplate.objects.filter(msg_type=0)
    context_object_name = 'smstemplate_list'
    filterset_class = SMSTemplateFilter


class SMSTemplateCreate(MyCreateView):
    template_name = 'admin/config/smstemplateadd.html'
    form_class = SMSTemplateForm
    model = SMSTemplate
    success_url = reverse_lazy('list_smstemplate_url')


class SMSTemplateUpdate(MyUpdateView):
    template_name = 'admin/config/smstemplatemodify.html'
    form_class = SMSTemplateForm
    model = SMSTemplate
    context_object_name = 'sms'
    success_url = reverse_lazy('list_smstemplate_url')


class SMSTemplateDelete(MyDeleteView):
    model = SMSTemplate


# =========站内信===========

class SiteLetterList(MyFilterView):
    template_name = 'admin/config/siteletterlist.html'
    queryset = SMSTemplate.objects.filter(msg_type=1)
    context_object_name = 'site_letter_list'
    filterset_class = SMSLogFilter


class SiteLetterCreate(MyCreateView):
    template_name = 'admin/config/sitelettertemplateadd.html'
    form_class = SMSTemplateForm
    model = SMSTemplate
    success_url = reverse_lazy('list_siteletter_url')

    def form_valid(self, form):
        template = form.save(commit=False)
        template.msg_type = 1
        template.save()
        return super(SiteLetterCreate, self).form_valid(form)


class SiteLetterUpdate(MyUpdateView):
    template_name = 'admin/config/sitelettertemplatemodify.html'
    form_class = SMSTemplateForm
    model = SMSTemplate
    context_object_name = 'sms'
    success_url = reverse_lazy('list_siteletter_url')


class SiteLetterDelete(MyDeleteView):
    model = SMSTemplate


# ==========站内消息日志=====

class SMSLogList(MyFilterView):
    template_name = 'admin/config/smsloglist.html'
    queryset = SMSSendLog.objects.all().order_by('-send_time')
    context_object_name = 'smssendlog_list'
    filterset_class = SMSLogFilter


class SMSLogDelete(MyDeleteView):
    model = SMSSendLog

def smslog_batch_delete(request):
    if not request.is_ajax():
        return ajax_fail(message='异常请求')
    ids = request.POST["ids"]
    id_list = ids.split(',')
    for id in id_list:
        if id == u'':
            continue
        smslog = SMSSendLog.objects.get_or_none(pk=int(id))
        if smslog:
            smslog.delete()
    messages.success(request, '记录删除成功')
    return ajax_ok(message='操作成功')


def add_message_log(user_id, sms_template):
    user = User.objects.get(pk=user_id)
    send_log = SMSSendLog()
    send_log.user = user
    send_log.template = sms_template
    send_log.send_content = sms_template.message_content
    send_log.send_mobile = user.mobile
    send_log.save()


# ====发送页面======
def sms_sendpage(request, id):
    sms = SMSTemplate.objects.get(pk=id)
    kw = {
        "tempid": id,
        "content": sms.message_content
    }
    return render(request, 'admin/config/smssend.html', kw)


def sms_send(request):
    tempid = request.POST["tempid"]
    to = request.POST["to"]
    to = to[:-1].split(",")
    sms_tem = SMSTemplate.objects.get(pk=tempid)
    send_user_list = User.objects.filter(pk__in=to)[:100]
    res_dic = dict()
    if send_user_list and sms_tem:
        if sms_tem.msg_type == 0:
            # 发送短信
            for user in send_user_list:
                res = SMSLogic(user).send_sms_by_template(tempid)
                res_dic.update({user.id: res})
        else:
            for user in send_user_list:
                add_message_log(user.id, sms_tem)
    return JsonResponse(res_dic)


# ====短信查询======

def basic_sms_config(request):
    sms_backend = SmsBackend()
    balance = sms_backend.get_balance()
    username = sms_backend.get_username()
    password = sms_backend.get_password()
    kw = {
        "company": u"北京亿美软通科技有限公司",
        "service_tel": u'400-779-7255',
        "balance": balance,
        "username": username,
        "password": password
    }
    return render(request, 'admin/config/smsinfo.html', kw)
