#!/usr/bin/env python
# -*- coding: utf-8 -*-
import ast
from django.core.urlresolvers import reverse, reverse_lazy
from ..forms.coach import *
from ..filter import CoachFilter, TrainTimeFilter
from .generic import *
from django.http import HttpResponseRedirect

# =============教练=============

class CoachList(MyFilterView):
    template_name = 'admin/coach/coachlist.html'
    queryset = User.objects.filter(is_superuser=False, role_type=2)
    context_object_name = 'coach_list'
    filterset_class = CoachFilter


class CoachCreate(MyCreateView):
    template_name = 'admin/coach/coachadd.html'
    form_class = CoachCreteForm
    model = User
    success_url = reverse_lazy('list_coach_url')

    def form_valid(self, form):
        user = form.save(commit=False)
        pwd = form.cleaned_data['id_card'][-6:]
        user.role_type = 2
        user.set_password(pwd)
        user.save()
        self.object = user
        return HttpResponseRedirect(self.get_success_url())


class CoachUpdate(MyUpdateView):
    template_name = 'admin/coach/coachmodify.html'
    form_class = CoachModifyForm
    model = User
    success_url = reverse_lazy('list_coach_url')

    def form_valid(self, form):
        old_user = self.get_object()
        user = form.save(commit=False)
        if old_user.password != user.password:
            user.set_password(user.password)
        user.save()
        return HttpResponseRedirect(self.get_success_url())


class CoachDelete(MyDeleteView):
    model = User

    def delete(self, request, *args, **kwargs):
        coach = self.get_object()
        coach_car_id = coach.coach_car.id
        queryset = User.objects.filter(coach_car_id=coach_car_id, role_type=1)
        if queryset.exists():
            raise ProtectedError(u"下面的会员还处于该教练名下，请先移除下面的会员信息", queryset)
        return super(CoachDelete, self).delete(request, *args, **kwargs)


# =============练车时间============

class TrainTimeList(MyFilterView):
    template_name = 'admin/coach/traintimelist.html'
    queryset = TrainTimeSpan.objects.all()
    context_object_name = 'traintime_list'
    filterset_class = TrainTimeFilter


class TrainTimeCreate(MyCreateView):
    template_name = 'admin/coach/traintimeadd.html'
    form_class = TrainTimeCreateForm
    model = TrainTimeSpan
    success_url = reverse_lazy('list_traintime_url')


class TrainTimeUpdate(MyUpdateView):
    template_name = 'admin/coach/traintimemodify.html'
    form_class = TrainTimeCreateForm
    model = TrainTimeSpan
    success_url = reverse_lazy('list_traintime_url')


class TrainTimeDelete(MyDeleteView):
    model = TrainTimeSpan
    success_url = reverse_lazy('list_traintime_url')

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        for item in CoachCar.objects.all().values('id', 'stage_two_train_time'):
            stage_two_train_time = u'[]' if not item['stage_two_train_time'] else item['stage_two_train_time']
            stage_two_train_time = ast.literal_eval(stage_two_train_time)
            id = str(self.object.id)
            if id in stage_two_train_time:
                stage_two_train_time.remove(id)
                coachcar = CoachCar.objects.get_or_none(pk=item['id'])
                if coachcar:
                    coachcar.stage_two_train_time = stage_two_train_time
                    coachcar.save()

        for item in CoachCar.objects.all().values('id', 'stage_three_train_time'):
            stage_three_train_time = u'[]' if not item['stage_three_train_time'] else item['stage_three_train_time']
            stage_three_train_time = ast.literal_eval(stage_three_train_time)
            id = str(self.object.id)
            if id in stage_three_train_time:
                stage_three_train_time.remove(id)
                coachcar = CoachCar.objects.get_or_none(pk=item['id'])
                if coachcar:
                    coachcar.stage_three_train_time = stage_three_train_time
                    coachcar.save()
        return super(TrainTimeDelete, self).delete(request, *args, **kwargs)
