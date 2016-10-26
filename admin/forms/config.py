#!/usr/bin/env python
# -*- coding: utf-8 -*-


from django import forms
from myforms import MyTimeInput, MyRadioFieldRenderer
from app.models import *


class SMSTemplateForm(forms.ModelForm):
    message_title = forms.CharField(max_length=50, label=u'模版名称', required=False,
                                    widget=forms.TextInput(attrs={'class': 'form-control'}))

    message_content = forms.CharField(max_length=300, label=u'模板内容', required=False,
                                      widget=forms.Textarea(attrs={'class': 'form-control'}))

    class Meta:
        model = SMSTemplate

        fields = ['message_title', 'message_content']


class ConfigForm(forms.ModelForm):
    reserve_overday = forms.IntegerField(label=u'可预约天数', required=True,
                                         widget=forms.TextInput(attrs={'class': 'form-control'}))

    is_open_blacklist = forms.ChoiceField(label=u'是否启用', initial=True,
                                          choices=((True, '是'), (False, '否')),
                                          widget=forms.RadioSelect(renderer=MyRadioFieldRenderer))

    blacklist_break = forms.IntegerField(label=u'黑名单爽约次数', required=True,
                                         widget=forms.TextInput(attrs={'class': 'form-control'}))

    close_start_time = forms.TimeField(label=u'禁止预约开始时间',
                                       widget=MyTimeInput(format=('%H:%M'),
                                                          attrs={'class': 'form-control timepicker'}))

    close_end_time = forms.TimeField(label=u'禁止预约结束时间',
                                     widget=MyTimeInput(format=('%H:%M'),
                                                        attrs={'class': 'form-control timepicker'}))

    class Meta:
        model = Config
        fields = ['reserve_overday', 'is_open_blacklist', 'blacklist_break', 'close_start_time', 'close_end_time']

