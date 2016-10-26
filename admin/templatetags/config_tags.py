# -*- coding: utf-8 -*-
from django import template
from app.models import User, TrainTimeSpan

register = template.Library()


@register.filter
def get_coach_name(coach_id):
    try:
        coach = User.objects.get(pk=coach_id)
        return coach.name
    except User.DoesNotExist:
        return '已删除'


@register.filter
def get_user_coach_name(user):
    try:
        car_id = user.coach_car.id
        coach = User.objects.filter(coach_car_id=car_id, role_type=2)[:1].get()
        return coach.name
    except User.DoesNotExist:
        return ""


@register.filter
def time_format(time):
    return str(time.hour) + u":00"


@register.filter
def cast_to_string(timespan_list):
    week_dic = {
        "0": "星期一",
        "1": "星期二",
        "2": "星期三",
        "3": "星期四",
        "4": "星期五",
        "5": "星期六",
        "6": "星期日",
    }
    result_str = ""
    for item in eval(timespan_list):
        result_str += week_dic[item] + "，"
    return result_str.rstrip("，")


@register.filter
def cast_traintime_to_string(traintime_list):
    result_str = ""
    for item in eval(traintime_list):
        train_time = TrainTimeSpan.objects.get_or_none(pk=item)
        if train_time:
            result_str += train_time.name + "，"
    return result_str.rstrip("，")
