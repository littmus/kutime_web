from django.shortcuts import render
from django.http import HttpResponse
from django.core import serializers
import json

from kutime.models.kutime import *

def index(request):
    list_col = College.objects.all()

    return render(
        request,
        'index.html',
        {
            'cols': list_col,
            'timetable_range': range(12),
        }
    )

def dept(request, col_num):
    data = None
    if col_num is not None:
        list_dept = Department.objects.filter(col__pk=col_num)
        data = serializers.serialize('json', list_dept, fields=('name'))
         
    return HttpResponse(data, mimetype='application/json')

def lec(request, dept_num):
    data = None
    if dept_num is not None:
        list_lec = Lecture.objects.filter(dept__pk=dept_num)
        data = serializers.serialize('json', list_lec)

    return HttpResponse(data, mimetype='application/json')

