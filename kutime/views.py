# -*- coding: utf-8 -*-
try:
    import simplejson as json
except ImportError:
    import json

from django.shortcuts import render
from django.http import HttpResponse
from django.core import serializers
from django.views.decorators.csrf import csrf_exempt
import watson

from models import *


def JsonResponse(json):
    return HttpResponse(json, content_type='application/json')

def index(request):
    list_col = College.objects.all()

    list_col_major_anam = list_col.filter(type='M', campus='A')
    list_col_major_sejong = list_col.filter(type='M', campus='S')
    list_col_etc_anam = list_col.filter(type='E', campus='A')
    list_col_etc_sejong = list_col.filter(type='E', campus='S')

    return render(
        request,
        'index.html',
        {
            'cols_major_anam': list_col_major_anam,
            'cols_major_sejong': list_col_major_sejong,
            'cols_etc_anam': list_col_etc_anam,
            'cols_etc_sejong': list_col_etc_sejong,
            'timetable_range': range(1, 13),
        }
    )

@csrf_exempt
def dept(request, col_num):
    data = None
    if col_num is not None:
        list_dept = Department.objects.filter(col__number=col_num)
        data = serializers.serialize('json', list_dept, fields=('name', 'number'))
         
    return JsonResponse(data)

@csrf_exempt
def lec(request, dept_num):
    data = None
    if dept_num is not None:
        if dept_num[0] in ['A', 'S']:
            campus = dept_num[0]
            num = dept_num[1:]
            list_lec = Lecture.objects.filter(col__campus=campus, dept__number=num)
        else:
            list_lec = Lecture.objects.filter(dept__number=dept_num)

        data = serializers.serialize('json', list_lec)

    return JsonResponse(data)

@csrf_exempt
def search(request):
    if request.method == 'GET':
        data = None
        q = request.GET.get('q', None)

        if q is not None:
            if u'교시' in q:
                pass

            if 'LP' in q:
                q = q.replace('LP', 'L-P')
                if u'관' in q:
                    q = q.replace(u'관', '')
#        for _q in q.split(','):
#            if q.endswith(u'교시'):
            #result = [s.object for s in watson.search(q)]
            """ TODO
                - 검색어 유형 따라 필터 적용
                  ex) 5교시 -> dayAndPeriod 에서만 검색
            """
            result = watson.filter(Lecture, q)
            data = serializers.serialize('json', result)
        
        return JsonResponse(data)
    else:
        return HttpResponse(status=404)
"""
from selenium import webdriver

def capture(request):
    if request.method == 'POST':
        drvier = webdriver.PhantomJS()
    else:
        return HttpResponse(status=404)
"""
