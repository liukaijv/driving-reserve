#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django import forms
from django.forms import ModelForm
from django.core.validators import RegexValidator
from myforms import MyCheckboxSelectMultiple, MyDateTimeInput, MyTimeInput
from app.models import *


class PlaceCreteForm(ModelForm):
    mobile_phone_regex = '^1\d{10}$|^(0\d{2,3}-?|\(0\d{2,3}\))?[1-9]\d{4,7}(-\d{1,8})?$'

    place_name = forms.CharField(max_length=100, label=u'训练场地', required=True,
                                 error_messages={('required', u'请输入场地名称'), },
                                 widget=forms.TextInput(attrs={'class': 'form-control'}))

    guard_name = forms.CharField(max_length=50, label=u'管理员姓名', required=False,
                                 widget=forms.TextInput(attrs={'class': 'form-control'}))

    guard_mobile = forms.CharField(max_length=20, label=u'管理员电话', required=False,
                                   validators=[
                                       RegexValidator(regex=mobile_phone_regex,
                                                      message=u'请输入正确的手机号码',
                                                      code='invalid_mobile'
                                       )
                                   ],
                                   widget=forms.TextInput(attrs={'class': 'form-control'}))

    address = forms.CharField(max_length=100, label=u'场地地址', required=False,
                              widget=forms.TextInput(attrs={'class': 'form-control'}))

    remarks = forms.CharField(max_length=300, label=u'备注信息', required=False,
                              widget=forms.Textarea(attrs={'cols': '25', 'rows': '5', 'class': 'form-control'}))

    class Meta:
        model = TrainingPlace
        # fields = []


class CoachCarCreateForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(CoachCarCreateForm, self).__init__(*args, **kwargs)
        self.fields["stage_three_train_time"].choices = TrainTimeSpan.objects.filter(exam_stage=3) \
            .values_list('id', 'name')
        self.fields["stage_two_train_time"].choices = TrainTimeSpan.objects.filter(exam_stage=2) \
            .values_list('id', 'name')

    TRAIN_TYPE = (
        ('', u'==请选择=='),
        ('C1', u'C1'),
        ('C2', u'C2'),
    )

    CAR_TYPE = (
        ('', u'==请选择=='),
        ('1', u'捷达'),
        ('2', u'桑塔纳'),
        ('3', u'新捷达'),
        ('4', u'新桑塔纳'),
        ('5', u'其他'),
    )

    license = forms.CharField(label=u'车辆牌照', required=True,
                              error_messages={'required': u'请输入车辆牌照.', },
                              widget=forms.TextInput(attrs={'class': 'form-control'}))

    train_type = forms.ChoiceField(label=u'车辆训练类型', choices=TRAIN_TYPE, required=True,
                                   error_messages={'required': u'请选择车辆训练类型.', },
                                   widget=forms.Select(attrs={'class': 'form-control'}))

    car_type = forms.ChoiceField(label=u'车辆种类', choices=CAR_TYPE, required=True,
                                 error_messages={'required': u'请选择车辆种类.', },
                                 widget=forms.Select(attrs={'class': 'form-control'}))

    training_place = forms.ModelChoiceField(queryset=TrainingPlace.objects.all(),
                                            empty_label=('', u'==请选择=='),
                                            cache_choices=True, required=True,
                                            widget=forms.Select(attrs={'class': 'form-control'}),
                                            label=u'车辆训练场地', to_field_name='id',
                                            initial='',
                                            error_messages={'required': u'请选择车辆训练场地.', }, )

    stage_two_train_time = forms.MultipleChoiceField(
        choices=TrainTimeSpan.objects.filter(exam_stage=2).values_list('id', 'name'),
        required=False,
        label=u'科目二训练时间', widget=MyCheckboxSelectMultiple)

    stage_three_train_time = forms.MultipleChoiceField(
        choices=TrainTimeSpan.objects.filter(exam_stage=3).values_list('id', 'name'),
        required=False,
        label=u'科目三训练时间', widget=MyCheckboxSelectMultiple)

    def __companre_times(self, two_times, three_times):
        flag = False
        for two_stage in two_times:
            two_start_time = two_stage["start_time"]
            two_end_time = two_stage["end_time"]

            for three_stage in three_times:
                three_start_time = three_stage["start_time"]
                three_end_time = three_stage["end_time"]
                flag = (two_end_time > three_start_time and two_start_time < three_end_time)
                if flag:
                    return True
        return flag


    def clean(self):
        cleaned_data = super(CoachCarCreateForm, self).clean()
        stage_two_train_time = cleaned_data.get("stage_two_train_time")
        stage_three_train_time = cleaned_data.get("stage_three_train_time")
        two_times = TrainTimeSpan.objects.filter(pk__in=stage_two_train_time, exam_stage=2) \
            .values('start_time', 'end_time')
        three_times = TrainTimeSpan.objects.filter(pk__in=stage_three_train_time, exam_stage=3) \
            .values('start_time', 'end_time')
        if self.__companre_times(two_times, three_times):
            raise forms.ValidationError(u"科目二和科目三时间段不能重复")
        return cleaned_data

    class Meta:
        model = CoachCar
        fields = ["license", "train_type", "car_type", "training_place", "stage_two_train_time",
                  "stage_three_train_time"]


class TrainTimeCreateForm(forms.ModelForm):
    name = forms.CharField(max_length=50, label=u'时段名称', required=False,
                           widget=forms.TextInput(attrs={'class': 'form-control'}))

    start_time = forms.CharField(label=u'开始时间', required=True,
                                 widget=MyTimeInput(format=('%H:%M'),
                                                    attrs={'class': 'form-control timepicker'}))

    end_time = forms.CharField(label=u'结束时间', required=True,
                               widget=MyTimeInput(format=('%H:%M'),
                                                  attrs={'class': 'form-control timepicker'}))

    class Meta:
        model = TrainTimeSpan
        fields = ['name', 'start_time', 'end_time']


class DisabledDateTimeCreteForm(ModelForm):
    begin_datetime = forms.CharField(label=u'开始时间', required=True,
                                     widget=MyDateTimeInput(format=('%Y%m%D %H:%M'),
                                                            attrs={'class': 'form-control',
                                                                   'data-format': 'yyyy-MM-dd hh:mm'}))

    end_datetime = forms.CharField(label=u'结束时间', required=True,
                                   widget=MyDateTimeInput(format=('%Y%m%D %H:%M'),
                                                          attrs={'class': 'form-control',
                                                                 'data-format': 'yyyy-MM-dd hh:mm'}))

    class Meta:
        model = DisabledDateTime
        fields = ['begin_datetime', 'end_datetime']
