#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.conf.urls import patterns, url

from admin.views.car import *
from admin.views.user import *
from admin.views.config import *
from admin.views.coach import *
from admin.views.reserve import *


# admin
urlpatterns = patterns('admin.views.admin',
                       url(r'^$', 'login', name='login_url'),
                       url(r'^index/$', 'index', name='home_url'),
                       url(r'^login/$', 'login', name='login_url'),
                       url(r'^logout/$', 'logout', name='logout_url'),
                       url(r'^changepwd/$', 'change_password', name='change_pwd_url'),
)

# car
urlpatterns += patterns('admin.views.car',
                        url(r'^car/add/$', CarCreate.as_view(), name='add_car_url'),
                        url(r'^car/list/$', CarList.as_view(), name='list_car_url'),
                        url(r'^car/modify/(?P<pk>\d+)/$', CarUpdate.as_view(), name='modify_car_url'),
                        url(r'^car/view/(?P<pk>\d+)/$', CarView.as_view(), name='view_car_url'),
                        url(r'^car/(?P<pk>\d+)/delete/$', CarDelete.as_view(), name='delete_car_url'),

                        url(r'^place/add/$', PlaceCreate.as_view(), name='add_place_url'),
                        url(r'^place/list/$', PlaceList.as_view(), name='list_place_url'),
                        url(r'^place/modify/(?P<pk>\d*)/$', PlaceUpdate.as_view(), name='modify_place_url'),
                        url(r'^place/(?P<pk>\d*)/delete/$', PlaceDelete.as_view(), name='delete_place_url'),

                        url(r'^caruse/(?P<pk>\d*)/list/$', CarUseList.as_view(), name='list_caruse_url'),
                        url(r'^caruse/(?P<pk>\d*)/add/$', CarUseCreate.as_view(), name='add_caruse_url'),
                        url(r'^caruse/(?P<pk>\d*)/delete/$', CarUseDelete.as_view(), name='delete_caruse_url'),
)

# coach
urlpatterns += patterns('admin.views.coach',
                        url(r'^coach/add/$', CoachCreate.as_view(), name='add_coach_url'),
                        url(r'^coach/list/$', CoachList.as_view(), name='list_coach_url'),
                        url(r'^coach/modify/(?P<pk>\d*)/$', CoachUpdate.as_view(), name='modify_coach_url'),
                        url(r'^coach/(?P<pk>\d*)/delete/$', CoachDelete.as_view(), name='delete_coach_url'),

                        url(r'^traintime/add/$', TrainTimeCreate.as_view(), name='add_traintime_url'),
                        url(r'^traintime/list/$', TrainTimeList.as_view(), name='list_traintime_url'),
                        url(r'^traintime/modify/(?P<pk>\d*)/$', TrainTimeUpdate.as_view(), name='modify_traintime_url'),
                        url(r'^traintime/(?P<pk>\d*)/delete/$', TrainTimeDelete.as_view(), name='delete_traintime_url'),
)

# config
urlpatterns += patterns('admin.views.config',
                        url(r'^basic/list/$', ConfigUpdate.as_view(), name='list_basic_url'),
                        url(r'^basic/sms/', 'basic_sms_config', name='list_sms_url'),
                        url(r'^smstemplate/list/$', SMSTemplateList.as_view(), name='list_smstemplate_url'),
                        url(r'^smstemplate/add/$', SMSTemplateCreate.as_view(), name='add_smstemplate_url'),
                        url(r'^smstemplate/modify/(?P<pk>\d*)/$', SMSTemplateUpdate.as_view(),
                            name='modify_smstemplate_url'),
                        url(r'^smstemplate/(?P<pk>\d*)/delete/$', SMSTemplateDelete.as_view(),
                            name='delete_smstemplate_url'),
                        url(r'^smslog/list/$', SMSLogList.as_view(), name='list_smslog_url'),
                        url(r'^smslog/(?P<pk>\d*)/delete/$', SMSLogDelete.as_view(), name='delete_smslog_url'),
                        url(r'^smslog/batch/delete/', 'smslog_batch_delete', name='batch_delete_smslog_url'),
                        url(r'^siteletter/list/$', SiteLetterList.as_view(), name='list_siteletter_url'),
                        url(r'^siteletter/add/$', SiteLetterCreate.as_view(), name='add_siteletter_url'),
                        url(r'^siteletter/modify/(?P<pk>\d*)/$', SiteLetterUpdate.as_view(),
                            name='modify_siteletter_url'),
                        url(r'^siteletter/(?P<pk>\d*)/delete/$', SiteLetterDelete.as_view(),
                            name='delete_siteletter_url'),
                        url(r'^sms/(?P<id>\d*)/sendpage/$', 'sms_sendpage', name='send_page_url'),
                        url(r'^sms/send/$', 'sms_send', name='send_sms_url')
)

# reserve
urlpatterns += patterns('admin.views.reserve',
                        url(r'^drive/add/$', 'drive_add', name='add_drive_reserve_url'),
                        url(r'^drive/list/$', DriveReserveList.as_view(), name='list_drive_reserve_url'),
                        url(r'^drive/check/$', 'drive_check', name='check_drive_reserve_url'),
                        url(r'^drive/(?P<pk>\d+)/delete/$', DriveReserveDelete.as_view(),
                            name='delete_drive_reserve_url'),
                        url(r'^drive/batch/delete/', 'drive_batch_delete', name='batch_delete_drive_url'),
                        url(r'^drive/batch/audit/', 'drive_batch_audit', name='batch_audit_drive_url'),
                        url(r'^drive/getform/$', 'reserve_form', name='form_drive_reserve_url'),
                        url(r'^drive/(?P<pk>\d+)/details/', DriveReserveDetail.as_view(), name='details_reserve_url'),

                        url(r'^exam/check/$', 'exam_check', name='check_exam_reserve_url'),
                        url(r'^exam/list/$', ExamReserveList.as_view(), name='list_exam_url'),
                        url(r'^exam/(?P<pk>\d*)/delete/$', ExamReserveDelete.as_view(), name='delete_exam_url'),
                        url(r'^exam/(?P<pk>\d+)/details/', ExamReserveDetail.as_view(), name='details_exam_url'),
                        url(r'^exam/batch/delete/', 'exam_batch_delete', name='batch_delete_exam_url'),
                        url(r'^exam/batch/audit/', 'exam_batch_audit', name='batch_audit_exam_url'),

                        url(r'^drive/notice/$', DriveReserveNotice.as_view(), name='notice_reserve_url'),
                        url(r'^drive/toggle_alert/$', drive_toggle_alert, name='drive_toggle_alert'),
)

# user
urlpatterns += patterns('admin.views.user',
                        url(r'^category/add/$', CategoryCreate.as_view(), name='add_category_url'),
                        url(r'^category/list/$', CategoryList.as_view(), name='list_category_url'),
                        url(r'^category/modify/(?P<pk>\d+)/$', CategoryUpdate.as_view(), name='modify_category_url'),
                        url(r'^category/(?P<pk>\d+)/delete/$', CategoryDelete.as_view(), name='delete_category_url'),

                        url(r'^feedback/list/$', FeedbackList.as_view(), name='list_feedback_url'),
                        url(r'^feedback/(?P<pk>\d*)/delete/$', FeedbackDelete.as_view(), name='delete_feedback_url'),
                        url(r'^feedback/details/(?P<pk>\d*)/$', FeedbackView.as_view(), name='details_feedback_url'),


                        url(r'^frequency/add/$', FrequencyCreate.as_view(), name='add_frequency_url'),
                        url(r'^frequency/list/$', FrequencyList.as_view(), name='list_frequency_url'),
                        url(r'^frequency/modify/(?P<pk>\d+)/$', FrequencyUpdate.as_view(), name='modify_frequency_url'),
                        url(r'^frequency/(?P<pk>\d+)/delete/$', FrequencyDelete.as_view(), name='delete_frequency_url'),

                        url(r'^user/add/$', UserCreate.as_view(), name='add_user_url'),

                        url(r'^user/list/search/$', 'get_user_list', name='list_user_search_url'),
                        url(r'^user/list/$', UserList.as_view(), name='list_user_url'),
                        url(r'^user/modify/(?P<pk>\d+)/$', UserUpdate.as_view(), name='modify_user_url'),
                        url(r'^user/view/(?P<pk>\d+)/$', UserView.as_view(), name='view_user_url'),
                        url(r'^user/modify/changestatus/', 'change_user_stage_status', name='change_user_url'),
                        url(r'^user/(?P<pk>\d*)/delete/', UserDelete.as_view(), name='delete_user_url'),

                        url(r'^user/blacklist/$', BlackList.as_view(), name='list_black_url'),
                        url(r'^user/blacklist/(?P<pk>\d*)/delete/$', BlackDelete.as_view(), name='delete_black_url'),
)

#
# urlpatterns += patterns('app.ajax',
# url(r'^ajax\/(?P<type>[A-Za-z]\w+)/$', 'ajax_handler'),
# )