#!/usr/bin/env python
# -*- coding: utf-8 -*-

import django_filters as df
from django_filters.widgets import RangeWidget
from django import forms
from app.models import *


class RangeField(forms.MultiValueField):
    widget = RangeWidget(attrs={
        'class': 'form-control datepicker',
        'style': 'border-radius:5px'
    })

    def __init__(self, *args, **kwargs):
        fields = (
            forms.DateField(),
            forms.DateField(),
        )
        super(RangeField, self).__init__(fields, *args, **kwargs)

    def compress(self, data_list):
        if data_list:
            return slice(*data_list)
        return None


class RangeFilter(df.Filter):
    field_class = RangeField

    def filter(self, qs, value):
        if value:
            if value.start and value.stop:
                lookup = '%s__range' % self.name
                return qs.filter(**{lookup: (value.start, value.stop)})
            else:
                if value.start:
                    qs = qs.filter(**{'%s__gte' % self.name: value.start})
                if value.stop:
                    qs = qs.filter(**{'%s__lte' % self.name: value.stop})
        return qs


def get_charfilter(label=u'', lookup_type='icontains'):
    return df.CharFilter(label=label, lookup_type=lookup_type,
                         widget=forms.TextInput(attrs={
                             'class': 'form-control',
                             'style': 'border-radius:5px',
                             'placeholder': label + u'搜索...'
                         }))


class PlaceFilter(df.FilterSet):
    place_name = get_charfilter(u'场地名称')
    guard_name = get_charfilter(u'负责人姓名')

    class Meta:
        model = TrainingPlace
        fields = ['place_name', 'guard_name']


class CoachCarFilter(df.FilterSet):
    license = get_charfilter(u'车牌号')
    training_place__place_name = get_charfilter(u'场地名称')

    class Meta:
        model = CoachCar
        fields = ['license', 'training_place__place_name']

class UserFilter(df.FilterSet):
    mobile = get_charfilter(u'手机号')
    name = get_charfilter(u'姓名')
    coach_car__license = get_charfilter(label=u'教练车')
    exam_stage = df.CharFilter(label=u'考试科目', lookup_type='icontains',
                               widget=forms.Select(choices=((("", "请选择"),) + EXAM_STAGE),
                                                   attrs={
                                                       'class': 'form-control',
                                                       'style': 'border-radius:5px',
                                                   }))
    exam_stage_status = df.CharFilter(label=u'科目状态', lookup_type='icontains',
                                      widget=forms.Select(choices=((("", "请选择"),) + EXAM_STAGE_STATUS),
                                                          attrs={
                                                              'class': 'form-control',
                                                              'style': 'border-radius:5px',
                                                          }))
    category__name = df.ModelChoiceFilter(label=u'教学模式', queryset=ClassCategory.objects.all(), empty_label=u'请选择',
                                          widget=forms.Select(
                                              attrs={'class': 'form-control', 'style': 'border-radius:5px', }
                                          ))

    register_time = df.CharFilter(label=u'报名时间', lookup_type='icontains',
                                  widget=forms.TextInput(attrs={
                                      'class': 'form-control datepicker',
                                      'style': 'border-radius:5px'
                                  }))

    class Meta:
        model = User
        fields = ['mobile', 'name', 'coach_car__license', 'exam_stage', 'exam_stage_status', 'category__name',
                  'register_time']


class BlackFilter(df.FilterSet):
    mobile = get_charfilter(u'手机号')
    name = get_charfilter(u'姓名')

    class Meta:
        model = User
        fields = ['mobile', 'name']


class CategoryFilter(df.FilterSet):
    name = get_charfilter(u'套餐名称')

    class Meta:
        model = ClassCategory
        fields = ['name', ]


class FrequencyFilter(df.FilterSet):
    name = get_charfilter(u'等级名称')

    class Meta:
        model = TrainFrequency
        fields = ['name', ]


class FeedBackFilter(df.FilterSet):
    mobile = get_charfilter(u'手机号码')

    class Meta:
        model = UserFeedback
        fields = ['mobile', ]


class SMSTemplateFilter(df.FilterSet):
    message_title = get_charfilter(u'模板类型')

    class Meta:
        model = SMSTemplate
        fields = ['message_title', ]


class SMSLogFilter(df.FilterSet):
    user_name = get_charfilter(u'学员姓名')
    template_message_category = get_charfilter(u'模板类型')
    send_mobile = get_charfilter(u'发送手机')

    class Meta:
        model = SMSTemplate
        fields = ['send_mobile', ]


class CoachFilter(df.FilterSet):
    name = get_charfilter(u'姓名')

    class Meta:
        model = User
        fields = ['name', ]


class TrainTimeFilter(df.FilterSet):
    name = get_charfilter(u'时段名称')

    class Meta:
        model = TrainTimeSpan
        fields = ['name', ]


AUDIT_STATUS = (
    ('', u'请选择'),
    (-1, u'审核不通过'),
    (0, u'待审核'),
    (1, u'审核通过')
)


class DriveReserveFilter(df.FilterSet):
    user__name = get_charfilter(u'姓名')
    user__mobile = get_charfilter(u'手机号')
    coach_car_license = df.ModelChoiceFilter(label=u'教学车辆', queryset=CoachCar.objects.all(), empty_label=u'请选择',
                                          widget=forms.Select(
                                              attrs={'class': 'form-control', 'style': 'border-radius:5px', }
                                          ))
    coach_name = get_charfilter(u'教练姓名')
    exam_stage = df.CharFilter(label=u'预约科目', lookup_type='icontains',
                               widget=forms.Select(choices=((("", "请选择"),) + EXAM_STAGE),
                                                   attrs={
                                                       'class': 'form-control',
                                                       'style': 'border-radius:5px',
                                                   }))

    audit_status = df.CharFilter(label=u'审核状态', lookup_type='icontains',
                                 widget=forms.Select(choices=AUDIT_STATUS,
                                                     attrs={
                                                         'class': 'form-control',
                                                         'style': 'border-radius:5px',
                                                     }))

    train_date = RangeFilter(label=u'预约日期', )

    class Meta:
        model = DriveReserve
        fields = ['user__name', 'user__mobile', 'coach_car_license', 'coach_name', 'exam_stage', 'train_date']


class ExamReserveFilter(df.FilterSet):
    name = get_charfilter(u'姓名')
    exam_stage = df.CharFilter(label=u'考试科目', lookup_type='icontains',
                               widget=forms.Select(choices=((("", "请选择"),) + EXAM_STAGE_STATUS),
                                                   attrs={
                                                       'class': 'form-control',
                                                       'style': 'border-radius:5px',
                                                   }))

    audit_status = df.CharFilter(label=u'审核状态', lookup_type='icontains',
                                 widget=forms.Select(choices=AUDIT_STATUS,
                                                     attrs={
                                                         'class': 'form-control',
                                                         'style': 'border-radius:5px',
                                                     }))

    class Meta:
        model = ExamReserve
        fields = ['name', 'exam_stage', 'audit_status']
