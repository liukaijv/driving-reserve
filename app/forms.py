# -*- coding: utf-8 -*-
from django import forms
from django.contrib import auth
from django.core.validators import RegexValidator

from app.models import *


class LoginUserForm(forms.Form):
    mobile_phone_regex = '^1\d{10}$|^(0\d{2,3}-?|\(0\d{2,3}\))?[1-9]\d{4,7}(-\d{1,8})?$'
    username = forms.CharField(error_messages={'required': u'账号不能为空'}, widget=forms.TextInput(
        attrs={'required': 'required', 'class': 'username', 'placeholder': u'输入你的手机号'}), validators=[
        RegexValidator(regex=mobile_phone_regex, message=u'请输入正确的手机号码', code='invalid_mobile')], )
    password = forms.CharField(error_messages={'required': u'密码不能为空'}, widget=forms.PasswordInput(
        attrs={'required': 'required', 'class': 'password', 'placeholder': u'默认身份证后6位'}))

    def __init__(self, request=None, *args, **kwargs):
        self.request = request
        self.user_cache = None

        super(LoginUserForm, self).__init__(*args, **kwargs)

    def clean(self):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')
        if username and password:
            user_exist = User.objects.filter(mobile=username).exists()
            if not user_exist:
                raise forms.ValidationError(u'您的账号不存在')
            self.user_cache = auth.authenticate(username=username, password=password)
            if self.user_cache is None:
                raise forms.ValidationError(u'账号和密码不匹配')
            if not self.user_cache.is_active:
                raise forms.ValidationError(u'你的账号已被禁用')

        return self.cleaned_data

    def get_user(self):
        return self.user_cache


# 投诉反馈
class FeedbackForm(forms.Form):
    """投诉反馈"""
    mobile_regex = '^1\d{10}$|^(0\d{2,3}-?|\(0\d{2,3}\))?[1-9]\d{4,7}(-\d{1,8})?$'
    mobile = forms.CharField(error_messages={'required': u'联系方式不能为空'}, validators=[
        RegexValidator(regex=mobile_regex,
                       message=u'请输入正确的手机号码',
                       code='invalid_mobile',
        )
    ], widget=forms.TextInput(attrs={'required': 'required'}))
    description = forms.CharField(error_messages={'required': u'投诉内容不能为空'},
                                  widget=forms.Textarea(attrs={'required': 'required'}))


# 考试申请
class ExamForm(forms.Form):
    """考试申请"""
    exam_stage = forms.CharField(error_messages={'required': u'请选择考试科目'},
                                 widget=forms.TextInput(attrs={'required': 'required'}))
    remarks = forms.CharField(error_messages={'required': u'备注信息不能为空'},
                              widget=forms.Textarea(attrs={'required': 'required'}))


# 生成预约单
class OrderForm(forms.Form):
    train_time_span = forms.IntegerField(required=True, error_messages={'required': u'预约时间段没有选择'})
    remarks = forms.CharField(required=False)


