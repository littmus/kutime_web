from django.shortcuts import render
from django.http import HttpResponse
from django.core import serializers
import json

from kutime.models.kutime import *

def JsonResponse(json):
    return HttpResponse(json, mimetype='application/json')

def index(request):
    list_col_major = College.objects.filter(type='M')
    list_col_etc = College.objects.filter(type='E')

    return render(
        request,
        'index.html',
        {
            'cols_major': list_col_major,
            'cols_etc': list_col_etc,
            'timetable_range': range(12),
        }
    )

def dept(request, col_num):
    data = None
    if col_num is not None:
        list_dept = Department.objects.filter(col__pk=col_num)
        data = serializers.serialize('json', list_dept, fields=('name'))
         
    return JsonResponse(data)

def lec(request, dept_num):
    data = None
    if dept_num is not None:
        list_lec = Lecture.objects.filter(dept__pk=dept_num)
        data = serializers.serialize('json', list_lec)

    return JsonResponse(data)


