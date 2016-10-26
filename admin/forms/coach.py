#!/usr/bin/env python
# -*- coding: utf-8 -*-
import time
from django import forms
from django.core.validators import RegexValidator
from myforms import MyTimeInput, MyRadioFieldRenderer
from app.models import *


class CoachCreteForm(forms.ModelForm):
    mobile_phone_regex = '^1\d{10}$|^(0\d{2,3}-?|\(0\d{2,3}\))?[1-9]\d{4,7}(-\d{1,8})?$'
    id_card_regex = "(^\d{15}$)|(^\d{18}$)|(^\d{17}(\d|X|x)$)"

    name = forms.CharField(max_length=50, label=u'姓名', required=True,
                           widget=forms.TextInput(attrs={'class': 'form-control'}))

    mobile = forms.CharField(max_length=20, label=u'手机号', required=True,
                             validators=[
                                 RegexValidator(regex=mobile_phone_regex,
                                                message=u'请输入正确的手机号码',
                                                code='invalid_mobile'
                                                )
                             ],
                             widget=forms.TextInput(attrs={'class': 'form-control'}))

    id_card = forms.CharField(max_length=20, label=u'身份证号', required=False,
                              validators=[
                                  RegexValidator(regex=id_card_regex,
                                                 message=u'请输入正确的身份证号',
                                                 code='invalid_id_card'
                                                 )
                              ],
                              widget=forms.TextInput(attrs={'class': 'form-control'}))

    age = forms.IntegerField(max_value=100, min_value=0, label=u'年龄',
                             widget=forms.TextInput(attrs={'class': 'form-control'}))

    sex = forms.ChoiceField(label=u'性别', choices=(('男', '男'), ('女', '女')),
                            widget=forms.Select(attrs={'class': 'form-control'}))

    coach_car = forms.ModelChoiceField(
        queryset=CoachCar.objects.exclude(id__in=[o.coach_car_id for o in User.objects.filter(role_type=2)]),
        empty_label=('', u'==请选择=='),
        cache_choices=True, required=True,
        widget=forms.Select(attrs={'class': 'form-control'}),
        label=u'教练车', to_field_name='id',
        initial='',
        error_messages={'required': u'请选择学员的教练车.', }, )

    remarks = forms.CharField(max_length=300, label=u'备注信息', required=False,
                              widget=forms.Textarea(attrs={'cols': '25', 'rows': '5', 'class': 'form-control'}))

    class Meta:
        model = User
        fields = ['name', 'mobile', 'id_card', 'age', 'sex', 'coach_car', 'remarks']


class CoachModifyForm(CoachCreteForm):
    coach_car = forms.ModelChoiceField(
        queryset=CoachCar.objects.all(),
        empty_label=('', u'==请选择=='),
        cache_choices=True, required=True,
        widget=forms.Select(attrs={'class': 'form-control'}),
        label=u'教练车', to_field_name='id',
        initial='',
        error_messages={'required': u'请选择学员的教练车.', }, )
    password = forms.CharField(label=u'密码',
                               widget=forms.PasswordInput(attrs={'class': 'form-control'}, render_value=True))
    is_active = forms.ChoiceField(label=u'是否启用', initial=True,
                                  choices=((True, '是'), (False, '否')),
                                  widget=forms.RadioSelect(renderer=MyRadioFieldRenderer))

    def clean_coach_car(self):
        coach_car = self.cleaned_data.get('coach_car', '')
        cur_user_id = self.instance.id
        other_car_exists = User.objects.filter(role_type=2, coach_car=coach_car.id).exclude(id=cur_user_id).exists()
        if other_car_exists:
            raise forms.ValidationError("该车辆已经关联其他教练。")
        return coach_car

    class Meta:
        model = User
        fields = ['name', 'mobile', 'id_card', 'age', 'sex', 'coach_car', 'password', 'remarks', 'is_active', ]


class TrainTimeCreateForm(forms.ModelForm):
    exam_stage = forms.ChoiceField(label=u'考试阶段', choices=((2, u'科目二'), (3, u'科目三')),
                                   widget=forms.Select(attrs={'class': 'form-control'}))

    name = forms.CharField(max_length=50, label=u'时段名称',
                           widget=forms.TextInput(attrs={'class': 'form-control'}))

    start_time = forms.CharField(label=u'开始时间', required=True,
                                 widget=MyTimeInput(format=('%H:%M'),
                                                    attrs={'class': 'form-control timepicker'}))

    end_time = forms.CharField(label=u'结束时间', required=True,
                               widget=MyTimeInput(format=('%H:%M'),
                                                  attrs={'class': 'form-control timepicker'}))

    def clean(self):
        cleaned_data = super(TrainTimeCreateForm, self).clean()
        start_t = time.strptime(cleaned_data.get("start_time"), "%H:%M")
        end_t = time.strptime(cleaned_data.get("end_time"), "%H:%M")
        if start_t >= end_t:
            raise forms.ValidationError(u"开始时间需小于结束时间")
        return cleaned_data

    class Meta:
        model = TrainTimeSpan
        fields = ['exam_stage', 'name', 'start_time', 'end_time']
