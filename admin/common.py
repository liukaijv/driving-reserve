#!/usr/bin/env python
# -*- coding: utf-8 -*-

import datetime
import decimal
import json
from django.http import HttpResponse
from django.utils.timezone import is_aware
from app.models import *
from smsglobal import SmsBackend
import logging

logger = logging.getLogger(__name__)


def adduserlog(user, operate, description="", is_background=True):
    userlog = UserLog()
    userlog.user_id = user.id
    userlog.is_background = is_background
    userlog.behavior = operate
    userlog.description = description
    userlog.save()


class DjangoJSONEncoder(json.JSONEncoder):
    """
    JSONEncoder subclass that knows how to encode date/time and decimal types.
    """

    def default(self, o):
        # See "Date Time String Format" in the ECMA-262 specification.
        if isinstance(o, datetime.datetime):
            r = o.isoformat()
            if o.microsecond:
                r = r[:23] + r[26:]
            if r.endswith('+00:00'):
                r = r[:-6] + 'Z'
            return r
        elif isinstance(o, datetime.date):
            return o.isoformat()
        elif isinstance(o, datetime.time):
            if is_aware(o):
                raise ValueError("JSON can't represent timezone-aware times.")
            r = o.isoformat()
            if o.microsecond:
                r = r[:12]
            return r
        elif isinstance(o, decimal.Decimal):
            return str(o)
        else:
            return super(DjangoJSONEncoder, self).default(o)


class JsonResponse(HttpResponse):
    def __init__(self, data, encoder=DjangoJSONEncoder, safe=True, **kwargs):
        if safe and not isinstance(data, dict):
            raise TypeError('In order to allow non-dict objects to be '
                            'serialized set the safe parameter to False')
        kwargs.setdefault('content_type', 'application/json')
        data = json.dumps(data, cls=encoder)
        super(JsonResponse, self).__init__(content=data, **kwargs)


class SMSLogic(object):
    """
    发送短信操作
    """
    REPLACE_LIST = [u"$学员姓名$", u"$教练姓名$", u"$教练电话$", u"$场地名称$", u"$场地地址$", u"$预约日期$", u"$预约时间$", u"$约考科目$"]

    def __init__(self, user):
        self.user = user

    def replace_flag_string(self, content, reserve_id=None, exam_reserve_id=None):
        user = self.user
        coach = User.objects.filter(role_type=2, coach_car_id=user.coach_car.id)[:1].get()

        if any(item in content for item in self.REPLACE_LIST):
            content = content.replace(u"$学员姓名$", user.name)
            content = content.replace(u"$教练姓名$", coach.name)
            content = content.replace(u"$教练电话$", coach.mobile)
            content = content.replace(u"$场地名称$", user.coach_car.training_place.place_name)
            content = content.replace(u"$场地地址$", user.coach_car.training_place.address)
            if reserve_id:
                reserve = DriveReserve.objects.get(pk=reserve_id)
                content = content.replace(u"$预约日期$", str(reserve.train_date))
                content = content.replace(u"$预约时间$",
                                          str(reserve.train_time_span_name) + u"【" +
                                          str(reserve.train_time_span_start_time.strftime('%H:%M')) +
                                          "-" +
                                          str(reserve.train_time_span_end_time.strftime('%H:%M')) + u"】")
            if exam_reserve_id:
                exam_reserve = ExamReserve.objects.get(pk=exam_reserve_id)
                content = content.replace(u"$约考科目$", str(exam_reserve.get_exam_stage_display()))
        return content

    def get_template(self, title):
        if title:
            try:
                return SMSTemplate.objects.get(message_title=title.strip())
            except SMSTemplate.DoesNotExist:
                return None
        else:
            return None

    def add_sms_log(self, template_id, content, mobile, is_suc):
        log = SMSSendLog()
        log.user_id = self.user.id
        log.template_id = template_id
        log.send_content = content
        log.send_mobile = mobile
        log.is_success = is_suc
        log.save()

    def send_sms_by_template(self, template_id, reserve_id=None, exam_reserve_id=None):
        to = self.user.mobile
        template = SMSTemplate.objects.get(pk=template_id)
        content = self.replace_flag_string(template.message_content, reserve_id, exam_reserve_id)
        if to and template_id:
            try:
                sms = SmsBackend()
                res = sms.send_messages(to=[to], body=content.encode())
                self.add_sms_log(template_id, content, to, res)
                logger.info(u"发送短信，电话号码：" + to + ",内容：" + content)
                return res
            except Exception as e:
                logger.error("发送短信失败，" + e.message)
                return False
        else:
            logger.error("send mobile or template id is None")
            raise Exception('send mobile or template id is None')

    def send_sms(self, title, reserve_id=None, exam_reserve_id=None):
        template = self.get_template(title)
        if not template:
            return False
        return self.send_sms_by_template(template.id, reserve_id, exam_reserve_id)

    def send_reserve_sms(self, reserve_id):
        reserve = DriveReserve.objects.get(pk=reserve_id)
        user = reserve.user
        exam_stage = user.exam_stage
        if exam_stage == 2:
            # 场地练习预约成功
            self.send_sms(u'预约通过审核', reserve_id)
        elif exam_stage == 3:
            # 路考练习预约成功
            self.send_sms(u'预约通过审核', reserve_id)

    def send_register_sms(self):
        self.send_sms(u'报名成功')

    def send_exam_reserve_sms(self, reserve_id):
        self.send_sms(u'预约考试通过审核', exam_reserve_id=reserve_id)

    def refuse_exam_reserve_sms(self, reserve_id):
        self.send_sms(u'预约考试不通过审核', exam_reserve_id=reserve_id)

    def refuse_reserve_sms(self, reserve_id):
        self.send_sms(u'预约未通过审核', reserve_id)

    def cancel_reserve_sms(self, reserve_id):
        self.send_sms(u'预约取消', reserve_id)

    # 科目一(预约考试，考试合格，考试不合格)
    def send_stage_one_reserve(self):
        self.send_sms(u'科目一约考成功')

    def send_stage_one_pass(self):
        self.send_sms(u'科目一考试合格')

    def send_stage_one_not_pass(self):
        self.send_sms(u'科目一考试不合格')

    # 科目二
    def send_stage_two_reserve(self):
        self.send_sms(u'科目二约考成功')

    def send_stage_two_pass(self):
        self.send_sms(u'科目二考试合格')

    def send_stage_two_not_pass(self):
        self.send_sms(u'科目二考试不合格')

    # 科目三
    def send_stage_three_reserve(self):
        self.send_sms(u'科目三约考成功')

    def send_stage_three_pass(self):
        self.send_sms(u'科目三考试合格')

    def send_stage_three_not_pass(self):
        self.send_sms(u'科目三考试不合格')

    # 科目四
    def send_stage_four_reserve(self):
        pass

    def send_stage_four_pass(self):
        self.send_sms(u'科目四考试合格')

    def send_stage_four_not_pass(self):
        pass

    def send_black_list_add(self):
        self.send_sms(u'被拉入黑名单提示')


class SMSFactory(object):
    user = None
    exam_stage = None
    logic = None

    def __init__(self, user):
        self.user = user
        self.exam_stage = user.exam_stage
        self.logic = SMSLogic(user)

    def send_reserve(self):
        try:
            if self.exam_stage == 1:
                self.logic.send_stage_one_reserve()
            elif self.exam_stage == 2:
                self.logic.send_stage_two_reserve()
            elif self.exam_stage == 3:
                self.logic.send_stage_three_reserve()
            elif self.exam_stage == 4:
                self.logic.send_stage_four_reserve()
            else:
                pass
        except:
            pass

    def send_pass(self):
        try:
            if self.exam_stage == 1:
                self.logic.send_stage_one_pass()
            elif self.exam_stage == 2:
                self.logic.send_stage_two_pass()
            elif self.exam_stage == 3:
                self.logic.send_stage_three_pass()
            elif self.exam_stage == 4:
                self.logic.send_stage_four_pass()
            else:
                pass
        except:
            pass

    def send_not_pass(self):
        try:
            if self.exam_stage == 1:
                self.logic.send_stage_one_not_pass()
            elif self.exam_stage == 2:
                self.logic.send_stage_two_not_pass()
            elif self.exam_stage == 3:
                self.logic.send_stage_three_not_pass()
            elif self.exam_stage == 4:
                self.logic.send_stage_four_not_pass()
            else:
                pass
        except:
            pass


class ReserveLogic(object):
    """
    预约
    """

    def reserve(self, user_id, date, time_id):
        if not date or not id:
            raise Exception('data or time is None')

        user = User.objects.get(pk=user_id)

        train_time = TrainTimeSpan.objects.get(pk=time_id)
        date = datetime.datetime.strptime(date, "%Y-%m-%d").date()
        reverse_start_datetime = datetime.datetime.combine(date, train_time.start_time)
        reverse_end_datetime = datetime.datetime.combine(date, train_time.end_time)
        # 取设定的预约时间
        config = Config.objects.all()[:1].get()
        reserve_overday = datetime.datetime.now() + datetime.timedelta(days=config.reserve_overday)
        car_id = user.coach_car.id
        # 车辆可用时间
        disabled_time = DisabledDateTime.objects.filter(
            coach_car_id=car_id,
            begin_datetime__lt=reverse_start_datetime,
            end_datetime__gt=reverse_end_datetime
        ).exists()
        drive_reserve = None
        coach = User.objects.filter(coach_car_id=car_id, role_type=2)[:1].get()
        if not disabled_time:
            drive_reserve = DriveReserve()
            drive_reserve.user_id = user_id
            drive_reserve.exam_stage = user.exam_stage
            drive_reserve.train_date = date
            drive_reserve.train_time_span_id = train_time.id
            drive_reserve.train_time_span_name = train_time.name
            drive_reserve.train_time_span_start_time = train_time.start_time
            drive_reserve.train_time_span_end_time = train_time.end_time

            drive_reserve.audit_status = 1
            drive_reserve.remarks = '管理员添加预约'
            drive_reserve.is_admin_reserve = True
            drive_reserve.coach_id = coach.id
            drive_reserve.coach_name = coach.name
            drive_reserve.coach_car_id = user.coach_car.id
            drive_reserve.coach_car_license = user.coach_car.license
            drive_reserve.training_place_id = user.coach_car.training_place.id
            drive_reserve.training_place_name = user.coach_car.training_place.place_name

            if reverse_start_datetime > reserve_overday:
                drive_reserve.is_admin_reserve = False
            drive_reserve.save()
        return drive_reserve

    def pass_reserve(self, reserve_id, remarks=''):
        drive_reserve = DriveReserve.objects.get(pk=reserve_id)
        drive_reserve.remarks = remarks
        drive_reserve.audit_status = 1
        drive_reserve.audit_time = datetime.datetime.now()
        drive_reserve.save()

    def refuse_reserve(self, reserve_id, remarks=''):
        drive_reserve = DriveReserve.objects.get(pk=reserve_id)
        drive_reserve.remarks = remarks
        drive_reserve.audit_time = datetime.datetime.now()
        drive_reserve.audit_status = -1
        drive_reserve.save()

    def cancel_reserve(self, reserve_id, remarks=''):
        drive_reserve = DriveReserve.objects.get(pk=reserve_id)
        drive_reserve.audit_status = -1
        drive_reserve.audit_time = datetime.datetime.now()
        drive_reserve.remarks = remarks
        drive_reserve.save()

    def delete_reserve(self, reserve_id, remarks=''):
        drive_reserve = DriveReserve.objects.get(pk=reserve_id)
        drive_reserve.delete()


class ExamReserveLogic(object):
    """
    预约考试
    """

    def pass_reserve(self, reserve_id):
        exam_reserve = ExamReserve.objects.get(pk=reserve_id)
        exam_reserve.audit_time = datetime.datetime.now()
        exam_reserve.audit_status = 1
        exam_reserve.save()

        user = exam_reserve.user
        user.exam_stage_status = 2
        user.save()

        adduserlog(user, u"修改科目状态", u"预约考试通过自动修改。学员科目状态被修改为：约考成功")

    def refuse_reserve(self, reserve_id):
        exam_reserve = ExamReserve.objects.get(pk=reserve_id)
        exam_reserve.audit_status = -1
        exam_reserve.audit_time = datetime.datetime.now()
        exam_reserve.save()
