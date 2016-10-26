# -*- coding: utf-8 -*-
from django import template

from app.models import User


register = template.Library()


@register.filter
def get_coach_name(user):
    car_id = user.coach_car.id
    coach = User.objects.filter(coach_car_id=car_id, role_type=2)[:1].get()
    if coach:
        return coach.name
    return ""
