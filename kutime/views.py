import json
from django.shortcuts import render
from django.http import HttpResponse
from django.core import serializers
from django.views.decorators.csrf import csrf_exempt

from kutime.models.kutime import *


def JsonResponse(json):
    return HttpResponse(json, mimetype='application/json')

def index(request):
    list_col_major = College.objects.filter(type='M')
    list_col_etc_anam = College.objects.filter(type='E', campus='A')
    list_col_etc_sejong = College.objects.filter(type='E', campus='S')

    return render(
        request,
        'index.html',
        {
            'cols_major': list_col_major,
            'cols_etc_anam': list_col_etc_anam,
            'cols_etc_sejong': list_col_etc_sejong,
            'timetable_range': range(12),
        }
    )

@csrf_exempt
def dept(request, col_num):
    data = None
    if col_num is not None:
        list_dept = Department.objects.filter(col__pk=col_num)
        data = serializers.serialize('json', list_dept, fields=('name'))
         
    return JsonResponse(data)

@csrf_exempt
def lec(request, dept_num):
    data = None
    if dept_num is not None:
        list_lec = Lecture.objects.filter(dept__pk=dept_num)
        data = serializers.serialize('json', list_lec)

    return JsonResponse(data)

