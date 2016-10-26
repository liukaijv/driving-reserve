#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.core.urlresolvers import reverse_lazy
from django.views.generic import *
from django_filters.views import FilterView
from ..forms.car import *
from ..filter import PlaceFilter, CoachCarFilter
from .generic import MyCreateView, MyUpdateView, MyDeleteView, MyFilterView


def addcoachcarlog(coach_car, operate, description="", is_background=True):
    coachcarlog = CoachCarLog()
    coachcarlog.coach_car = coach_car
    coachcarlog.is_background = is_background
    coachcarlog.behavior = operate
    coachcarlog.description = description
    coachcarlog.save()


# =============教练车==================

class CarList(MyFilterView):
    template_name = 'admin/car/carlist.html'
    queryset = CoachCar.objects.all()
    context_object_name = 'car_list'
    filterset_class = CoachCarFilter


class CarCreate(MyCreateView):
    template_name = 'admin/car/caradd.html'
    form_class = CoachCarCreateForm
    model = CoachCar
    success_url = reverse_lazy('list_car_url')

    def form_valid(self, form):
        ret = super(CarCreate, self).form_valid(form)
        addcoachcarlog(self.object, "添加车辆")
        return ret


class CarUpdate(MyUpdateView):
    template_name = 'admin/car/carmodify.html'
    form_class = CoachCarCreateForm
    model = CoachCar
    success_url = reverse_lazy('list_car_url')

    def form_valid(self, form):
        old_car = self.get_object()
        car = form.save(commit=False)
        if car.stage_two_train_time == "":
            car.stage_two_train_time = "[]"
        if car.stage_three_train_time == "":
            car.stage_three_train_time = "[]"

        description = ""
        if old_car.license != car.license:
            description += u"姓名:(" + old_car.license + "->" + car.license + ");"
        if old_car.train_type != car.train_type:
            description += u"训练类型:(" + old_car.get_train_type_display() + "->" + car.get_train_type_display() + ");"
        if old_car.car_type != car.car_type:
            description += u"车辆种类:(" + old_car.get_car_type_display() + "->" + car.get_car_type_display() + ");"
        if old_car.training_place != car.training_place:
            description += u"训练场地:(" + str(old_car.training_place) + "->" + str(car.training_place) + ");"
        if old_car.stage_two_train_time != car.stage_two_train_time:
            description += u"科目二训练时间:(" + str(old_car.stage_two_train_time) + "->" + str(
                car.stage_two_train_time) + ");"
        if old_car.stage_three_train_time != car.stage_three_train_time:
            description += u"科目三训练时间:(" + str(old_car.stage_three_train_time) + "->" + str(
                car.stage_three_train_time) + ");"
        addcoachcarlog(old_car, u"修改车辆信息", description)
        return super(CarUpdate, self).form_valid(form)


class CarView(DetailView):
    template_name = 'admin/car/carview.html'
    model = CoachCar


class CarDelete(MyDeleteView):
    model = CoachCar


# =============教练车场地===================

class PlaceList(MyFilterView):
    template_name = 'admin/car/placelist.html'
    queryset = TrainingPlace.objects.all()
    context_object_name = 'place_list'
    filterset_class = PlaceFilter


class PlaceCreate(MyCreateView):
    template_name = 'admin/car/placeadd.html'
    form_class = PlaceCreteForm
    model = TrainingPlace
    success_url = reverse_lazy('list_place_url')


class PlaceUpdate(MyUpdateView):
    template_name = 'admin/car/placemodify.html'
    form_class = PlaceCreteForm
    model = TrainingPlace
    success_url = reverse_lazy('list_place_url')


class PlaceDelete(MyDeleteView):
    model = TrainingPlace


# ====教练车不能使用====

class CarUseList(MyFilterView):
    template_name = 'admin/car/caruselist.html'

    context_object_name = 'caruse_list'
    filterset_class = CoachCarFilter

    def get_queryset(self):
        pk = self.kwargs.get("pk", None)
        return DisabledDateTime.objects.filter(coach_car=pk)


    def get_context_data(self, **kwargs):
        context = super(CarUseList, self).get_context_data(**kwargs)
        pk = self.kwargs.get("pk", None)
        context["coach_car"] = CoachCar.objects.get(pk=pk)
        return context


class CarUseCreate(MyCreateView):
    template_name = 'admin/car/caruseadd.html'
    form_class = DisabledDateTimeCreteForm
    model = DisabledDateTime

    def get_success_url(self):
        return reverse_lazy('list_caruse_url', kwargs={'pk': self.kwargs.get("pk", None)})

    def form_valid(self, form):
        pk = self.kwargs.get("pk", None)
        coach_car = CoachCar.objects.get(pk=pk)
        model = form.save(commit=False)
        model.coach_car_id = coach_car.id
        model.save()
        self.object = model
        description = "车辆添加禁用时间：( " + str(model) + ");"
        addcoachcarlog(coach_car, "添加禁用时间", description)
        return super(CarUseCreate, self).form_valid(form)


class CarUseDelete(MyDeleteView):
    model = DisabledDateTime

    def delete(self, request, *args, **kwargs):
        obj = self.get_object()
        ret = super(CarUseDelete, self).delete(request, *args, **kwargs)
        coach_car = CoachCar.objects.get(pk=obj.coach_car_id)
        addcoachcarlog(coach_car, "车辆删除禁用时间", "车辆添加禁用时间:(" + str(obj) + ")")
        return ret




