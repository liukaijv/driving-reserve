#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.conf.urls import patterns, url

from app.forms import *


# 页面
urlpatterns = patterns('app.views',
                       url(r'^$', 'login'),
                       url(r'^login/$', 'login', name='login'),
                       url(r'^logout/$', 'logout', name='logout'),
                       url(r'^student_profile/$', 'student_profile', name='student_profile'),
                       url(r'^coach_profile/$', 'coach_profile', name='coach_profile'),
                       url(r'^feedback/$', 'feedback', name='feedback'),
                       url(r'^message_list/$', 'message_list', name='message_list'),
                       url(r'^reserver/$', 'reserver', name='reserver'),
                       url(r'^forget_password/$', 'forget_password', name='forget_password'),
                       url(r'^exam/$', 'exam', name='exam'),
                       url(r'^load_reserver_data_student/$', 'load_reserver_data_student',
                           name='load_reserver_data_student'),
                       url(r'^load_reserver_data_coach/$', 'load_reserver_data_coach', name='load_reserver_data_coach'),
                       url(r'^load_reserver_data/$', 'load_reserver_data', name='load_reserver_data'),
)

# ajax请求
urlpatterns += patterns('app.ajax',
                        url(r'^feedback_validate/$', 'ajax_validate', {'form_class': FeedbackForm},
                            'feedback_validate'),
                        url(r'^login_validate/$', 'ajax_validate', {'form_class': LoginUserForm}, 'login_validate'),
                        url(r'^exam_validate/$', 'ajax_validate', {'form_class': ExamForm}, 'exam_validate'),
                        url(r'^order_validate/$', 'ajax_validate', {'form_class': OrderForm}, 'order_validate'),
                        url(r'^do_login/$', 'do_login', name='do_login'),
                        url(r'^order_action/$', 'order_action', name='order_action'),
                        url(r'^change_sign_status/$', 'change_sign_status', name='change_sign_status'),
                        url(r'^confirm_order_condition/$', 'confirm_order_condition', name='confirm_order_condition'),
                        url(r'^order_view/$', 'order_view', name='order_view'),
                        url(r'^do_feedback/$', 'do_feedback', name='do_feedback'),
                        url(r'^message_view/$', 'message_view', name='message_view'),
                        url(r'^message_delete/$', 'message_delete', name='message_delete'),
                        url(r'^do_exam/$', 'do_exam', name='do_exam'),
)