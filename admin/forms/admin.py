#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django import forms
from django.contrib import auth
from django.contrib.auth import get_user_model

from app.models import User


class LoginUserForm(forms.Form):
    username = forms.CharField(label=u'用户名', error_messages={'required': u'用户名不能为空'},
                               widget=forms.TextInput(
                                   attrs={'class': 'form-control', }
                               ))
    password = forms.CharField(label=u'密 码', error_messages={'required': u'密码不能为空'},
                               widget=forms.PasswordInput(
                                   attrs={'class': 'form-control', }
                               ))

    def __init__(self, request=None, *args, **kwargs):
        self.request = request
        self.user_cache = None

        super(LoginUserForm, self).__init__(*args, **kwargs)

    def clean_password(self):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')

        if username and password:
            self.user_cache = auth.authenticate(username=username, password=password)
            if self.user_cache is None:
                raise forms.ValidationError(u'账号密码不匹配')
            elif not self.user_cache.is_active:
                raise forms.ValidationError(u'此账号已被禁用')
        return self.cleaned_data

    def get_user(self):
        return self.user_cache


class ChangePasswordForm(forms.Form):
    old_password = forms.CharField(label=u'原始密码', error_messages={'required': '请输入原始密码'},
                                   widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    new_password1 = forms.CharField(label=u'新密码', error_messages={'required': '请输入新密码'},
                                    widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    new_password2 = forms.CharField(label=u'重复输入', error_messages={'required': '请重复新输入密码'},
                                    widget=forms.PasswordInput(attrs={'class': 'form-control'}))

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super(ChangePasswordForm, self).__init__(*args, **kwargs)

    def clean_old_password(self):
        old_password = self.cleaned_data["old_password"]
        if not self.user.check_password(old_password):
            raise forms.ValidationError(u'原密码错误')
        return old_password

    def clean_new_password2(self):
        password1 = self.cleaned_data.get('new_password1')
        password2 = self.cleaned_data.get('new_password2')
        if len(password1) < 6:
            raise forms.ValidationError(u'密码必须大于6位')

        if password1 and password2:
            if password1 != password2:
                raise forms.ValidationError(u'两次密码输入不一致')
        return password2

    def save(self, commit=True):
        self.user.set_password(self.cleaned_data['new_password1'])
        if commit:
            self.user.save()
        return self.user
