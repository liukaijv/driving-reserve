#!/usr/bin/env python
# -*- coding: utf-8 -*-

from itertools import chain

from django import forms
from django.core.validators import RegexValidator
from myforms import MyCheckboxSelectMultiple, MyRadioFieldRenderer
from app.models import *


class UserCreteForm(forms.ModelForm):
    mobile_phone_regex = '^1\d{10}$|^(0\d{2,3}-?|\(0\d{2,3}\))?[1-9]\d{4,7}(-\d{1,8})?$'
    id_card_regex = "(^\d{15}$)|(^\d{18}$)|(^\d{17}(\d|X|x)$)"

    name = forms.CharField(max_length=50, label=u'姓名', required=True,
                           widget=forms.TextInput(attrs={'class': 'form-control'}))

    id_card = forms.CharField(max_length=20, label=u'身份证号', required=True,
                              validators=[
                                  RegexValidator(regex=id_card_regex,
                                                 message=u'请输入正确的身份证号',
                                                 code='invalid_id_card'
                                  )
                              ],
                              widget=forms.TextInput(attrs={'class': 'form-control'}))

    mobile = forms.CharField(max_length=20, label=u'手机号', required=True,
                             validators=[
                                 RegexValidator(regex=mobile_phone_regex,
                                                message=u'请输入正确的手机号码',
                                                code='invalid_mobile'
                                 ),
                             ],
                             widget=forms.TextInput(attrs={'class': 'form-control'}))

    age = forms.IntegerField(max_value=100, min_value=0, label=u'年龄',
                             widget=forms.TextInput(attrs={'class': 'form-control'}))

    sex = forms.ChoiceField(label=u'性别', choices=((u'男', u'男'), (u'女', u'女')),
                            widget=forms.Select(attrs={'class': 'form-control'}))

    register_time = forms.DateField(label=u'报名时间',
                                    widget=forms.DateInput(format='%Y-%m-%d',
                                                           attrs={'class': 'form-control datepicker'}))

    train_frequency = forms.ModelChoiceField(queryset=TrainFrequency.objects.all(),
                                             empty_label=('', u'==请选择=='),
                                             cache_choices=True, required=True,
                                             widget=forms.Select(attrs={'class': 'form-control'}),
                                             label=u'学员等级', to_field_name='id',
                                             initial='',
                                             error_messages={'required': u'请选择学员的等级.', }, )

    exam_stage = forms.ChoiceField(label=u'考试阶段', choices=EXAM_STAGE,
                                   widget=forms.Select(attrs={'class': 'form-control'}))

    category = forms.ModelChoiceField(queryset=ClassCategory.objects.all(),
                                      empty_label=('', u'==请选择=='),
                                      cache_choices=True, required=True,
                                      widget=forms.Select(attrs={'class': 'form-control'}),
                                      label=u'教学模式', to_field_name='id',
                                      initial='',
                                      error_messages={'required': u'请选择教学模式.', }, )

    coach_car = forms.ModelChoiceField(queryset=CoachCar.objects.all(),
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
        fields = ['name', 'id_card', 'mobile', 'age', 'sex', 'register_time', 'train_frequency',
                  'exam_stage', 'category', 'coach_car']

    def clean_mobile(self):
        mobile = self.cleaned_data['mobile']
        qs = User.objects.filter(mobile=mobile)
        if self.instance.id:
            qs = qs.exclude(pk=self.instance.id)
        if qs.count() > 0:
            raise forms.ValidationError('该电话号码已经被使用.')
        return mobile

    def clean_id_card(self):
        id_card = self.cleaned_data['id_card']
        qs = User.objects.filter(id_card=id_card)
        if self.instance.id:
            qs = qs.exclude(pk=self.instance.id)
        if qs.count() > 0:
            raise forms.ValidationError('该身份证号已经被使用.')
        return id_card


class UserModifyForm(UserCreteForm):
    password = forms.CharField(label=u'密码',
                               widget=forms.PasswordInput(render_value=True, attrs={'class': 'form-control'}))
    is_active = forms.ChoiceField(label=u'是否启用', initial=True,
                                  choices=((True, '是'), (False, '否')),
                                  widget=forms.RadioSelect(renderer=MyRadioFieldRenderer))

    class Meta:
        model = User
        fields = ['name', 'id_card', 'mobile', 'age', 'sex', 'register_time', 'train_frequency',
                  'exam_stage', 'category', 'coach_car', 'password', 'is_active']


class CategoryCreateForm(forms.ModelForm):
    WEEK_DAYS = (
        ('0', u'星期一'),
        ('1', u'星期二'),
        ('2', u'星期三'),
        ('3', u'星期四'),
        ('4', u'星期五'),
        ('5', u'星期六'),
        ('6', u'星期日'),
    )
    name = forms.CharField(max_length=50, label=u'套餐名称', required=False,
                           widget=forms.TextInput(attrs={'class': 'form-control'}),
                           error_messages={'required': u'套餐名称不能为空.', })

    fee = forms.DecimalField(label=u'费用', max_digits=7, decimal_places=2,
                             widget=forms.TextInput(attrs={'class': 'form-control'}),
    )

    # 训练周期,列表存储
    training_weekdays = forms.MultipleChoiceField(choices=WEEK_DAYS, required=True, label=u'套餐时间',
                                                  widget=MyCheckboxSelectMultiple)

    remarks = forms.CharField(max_length=300, label=u'备注信息', required=False,
                              widget=forms.Textarea(attrs={'cols': '25', 'rows': '5', 'class': 'form-control'}))

    class Meta:
        model = ClassCategory
        fields = ['name', 'fee', 'training_weekdays', 'remarks']


class FrequencyCreateForm(forms.ModelForm):
    name = forms.CharField(max_length=50, label=u'等级名称', required=False,
                           widget=forms.TextInput(attrs={'class': 'form-control'}))
    # 每天的预约次数
    day_reserve_count = forms.IntegerField(label=u'每天的预约次数', required=True,
                                           widget=forms.TextInput(attrs={'class': 'form-control'}))
    # 每周的预约次数
    week_reserve_count = forms.IntegerField(label=u'每周的预约次数', required=True,
                                            widget=forms.TextInput(attrs={'class': 'form-control'}))

    # 每月的周末最多预约次数
    mouth_weekend_reserve_count = forms.IntegerField(label=u'月周末最多预约次数', required=True,
                                                     widget=forms.TextInput(attrs={'class': 'form-control'}))

    class Meta:
        model = TrainFrequency
        fields = ['name', 'day_reserve_count', 'week_reserve_count', 'mouth_weekend_reserve_count', ]