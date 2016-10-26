#!/usr/bin/env python
# -*- coding: utf-8 -*-
# created by yangxiaodong1214@126.com on 2015-06-02.
from itertools import chain
import ast
from django import forms
from django.forms.util import flatatt
from django.utils.encoding import force_text
from django.utils.safestring import mark_safe
from django.forms.widgets import RadioFieldRenderer
from django.utils.html import format_html, format_html_join


class MyTimeInput(forms.TimeInput):
    def render(self, name, value, attrs=None):
        if value is None:
            value = ''
        final_attrs = self.build_attrs(attrs, type=self.input_type, name=name)
        if value != '':
            final_attrs['value'] = force_text(self._format_value(value))
        return format_html('<div class="input-group bootstrap-timepicker">'
                           + '<input{0} />'
                           + '<span class="input-group-addon add-on entypo-clock"></span></div>',
                           flatatt(final_attrs))


class MyDateTimeInput(forms.DateTimeInput):
    def render(self, name, value, attrs=None):
        if value is None:
            value = ''
        final_attrs = self.build_attrs(attrs, type=self.input_type, name=name)
        if value != '':
            final_attrs['value'] = force_text(self._format_value(value))
        return format_html('<div class="input-group datetimepicker">'
                           + '<input{0} />'
                           + '<span class="input-group-addon add-on">'
                           + '<i class="entypo-calendar" data-time-icon="entypo-clock" data-date-icon="entypo-calendar"></i>'
                           + '</span>'
                           + '</div>',
                           flatatt(final_attrs))


class MyRadioFieldRenderer(RadioFieldRenderer):
    def render(self):
        return format_html('<ul class="list like-radio">\n{0}\n</ul>',
                           format_html_join('\n', '<li>{0}</li>',
                                            [(force_text(w),) for w in self]))


class MyCheckboxSelectMultiple(forms.CheckboxSelectMultiple):
    def render(self, name, value, attrs=None, choices=()):
        if not value: value = '[]'
        has_id = attrs and 'id' in attrs
        final_attrs = self.build_attrs(attrs, name=name)
        output = ['<ul class="list" style="float:none;margin-top:15px;">']
        str_values = eval(str(value))
        for i, (option_value, option_label) in enumerate(chain(self.choices, choices)):
            if has_id:
                final_attrs = dict(final_attrs, id='%s_%s' % (attrs['id'], i))
                label_for = format_html(' for="{0}"', final_attrs['id'])
            else:
                label_for = ''
            cb = forms.CheckboxInput(final_attrs, check_test=lambda value: value in str_values)
            option_value = force_text(option_value)
            rendered_cb = cb.render(name, option_value, attrs={"style": "position: absolute; opacity: 0;", })
            option_label = force_text(option_label)
            out_html = u'<li><div class="icheckbox_flat-red" style="position: relative;display:inline-block;">{1}</div><label style="margin:3px 0 10px 4px;vertical-align:top;" {0}>{2}</label></li>'
            out = format_html(out_html, label_for, rendered_cb, option_label)
            output.append(out)
        output.append('</ul>')
        return mark_safe('\n'.join(output))
