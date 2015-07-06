# -*- coding:utf-8 -*-

import os,sys
import time
import re
import requests
from bs4 import BeautifulSoup as bs

import django

os.environ['DJANGO_SETTINGS_MODULE'] = 'kutime.settings'
django.setup()
from kutime.models import *

URL_MAJOR = 'http://sugang.korea.ac.kr/lecture/LecMajorSub.jsp'
URL_ETC = 'http://sugang.korea.ac.kr/lecture/LecEtcSub.jsp'
URL_GRADUATE = 'http://sugang.korea.ac.kr/lecture/LecGradMajorSub.jsp'
URL_DEPT_MAJOR = 'http://sugang.korea.ac.kr/lecture/LecDeptPopup.jsp?frm=frm_ms&colcd=%(colcd)s&deptcd=%(deptcd)s&dept=%(dept)s&year=%(year)s&term=%(term)s'
URL_DEPT_ETC = 'http://sugang.korea.ac.kr/lecture/LecDeptPopup.jsp?frm=frm_ets&colcd=%(colcd)s&deptcd=%(deptcd)s&dept=%(dept)s'
URL_DEPT_GRADUATE = 'http://sugang.korea.ac.kr/lecture/LecDeptPopup.jsp?frm=frm_gms&colcd=%(colcd)s&deptcd=%(deptcd)s&dept=%(dept)s'

RE_DEPT = re.compile(u'el.style.color = "black";\r\n\t\t\tel.selected = "(true|)";  \r\n            el.value ="(?P<num>\d{2,4})";\r\n            el.text = "(?P<name>[\(\)\uac00-\ud7a3\w ·]+)";', re.UNICODE)

# 세종 캠퍼스 과목중에 빨간색으로 된 dept에 속한 과목들이 있음 (심층 영어)
#RE_DEPT_ETC = re.compile(u'el.style.color = "black";\r\n            el.value ="(?P<num>\d{2,4})";\r\n            el.text = "(?P<name>[\(\)\uac00-\ud7a3\w ·]+)";', re.UNICODE)
RE_DEPT_ETC = re.compile(u'el.value ="(?P<num>\d{2,4})";\r\n            el.text = "(?P<name>[\(\)\uac00-\ud7a3\w ·]+)";', re.UNICODE)

RE_DC = re.compile(u'(?P<day>[\uac00-\ud7a3]{1}\([\d-]+\)) (?P<classroom>[\uac00-\ud7a3\w\d\- ]*(?=[\uac00-\ud7a3\w\d\- ])\d\S)', re.UNICODE)
RE_DC_DAYONLY = re.compile(u'(?P<day>[\uac00-\ud7a3]{1}\([\d-]+\))', re.UNICODE)

YEAR = 2015
SEMESTER = '2R'
"""
1R
1S
2R
2W
SC
"""

MAJOR = 'M'
ETC = 'E'
ANAM = 'A'
SEJONG = 'S'
GRADUATE = 'G'

DEBUG = False
global_error_list = []

session = requests.Session()
session.mount('http://sugang.korea.ac.kr', requests.adapters.HTTPAdapter(max_retries=10))

def index(_type, campus=None, lang='KOR'):
    if _type == MAJOR:
        URL = URL_MAJOR
        URL_DEPT = URL_DEPT_MAJOR
        TABLE_INDEX = 0
    elif _type == ETC:
        URL = URL_ETC
        URL_DEPT = URL_DEPT_ETC
        TABLE_INDEX = 0
    elif _type == GRADUATE:
        URL = URL_GRADUATE
        URL_DEPT = URL_DEPT_GRADUATE
        TABLE_INDEX = -1

    r = session.get(URL, params={'lang':lang})
    soup = bs(r.content)
    cols = soup.find('select', attrs={'name':'col'})

    for col in cols.find_all('option'): 
        if 'red' in str(col):
            continue
        
        number = col['value']
        name = col.text.strip()
        
        if DEBUG:
            print number, name

        current_col, created = College.objects.get_or_create(number=number, name=name, type=_type, campus=campus)
        if not DEBUG and not created:
            current_col.save()

        #print name

        if _type == MAJOR:
            dept_url = URL_DEPT % {'colcd':number, 'deptcd':'', 'dept':'dept', 'year':YEAR, 'term':SEMESTER}
        elif _type == ETC:
            dept_url = URL_DEPT % {'colcd':number, 'deptcd':'', 'dept':'dept'}
        elif _type == GRADUATE:
            dept_url = URL_DEPT % {'colcd':number, 'deptcd':'', 'dept':'dept'}
            #pass
        
        if DEBUG:
            print dept_url
        
        r = session.get(dept_url)
        _soup = bs(r.content)
        depts = _soup.find('script')

        if _type == MAJOR:
            m = [m.groupdict() for m in RE_DEPT.finditer(depts.text)]
        elif _type == ETC: 
            m = [m.groupdict() for m in RE_DEPT_ETC.finditer(depts.text)]
        elif _type == GRADUATE:
            m = [m.groupdict() for m in RE_DEPT.finditer(depts.text)]
    	
        if len(m) == 0:
            if _type == MAJOR:
                continue
            elif _type == ETC:
                m.append({'num': '_'+number, 'name': name,})
            elif _type == GRADUATE:
                continue

        for dept in m:
            dept_num = str(dept['num'])
            dept_name = dept['name'].strip()
            
            if DEBUG:
                print dept_name
            
            current_dept, created = Department.objects.get_or_create(col=current_col, number=dept_num, name=dept_name)
            params = {
                'yy': YEAR,
                'tm': SEMESTER,
                'col': number,
                'dept': dept_num,
                'lang': lang,
            }

            if _type == ETC:
                if dept_num[1:] == number:
                    del params['dept']

                params['campus'] = '1' if campus == ANAM else '2'

            r = session.post(URL, params=params)
            lec_soup = bs(r.content)
            if lec_soup.find('div', class_='error'):
                continue
            
            table = lec_soup.find_all('table')[TABLE_INDEX]
            if not DEBUG and not created:
                current_dept.save()

            try:
                lec_info = None
                for lec_row in table.find_all('tr')[1:]:
                    lec_info = lec_row.find_all('td')

                    if _type == MAJOR:
                        lec_campus = lec_info.pop(0)
                        if current_col.campus is None:
                            current_col.campus = ANAM if lec_campus.text == u'안암' else SEJONG
                            current_col.save()

                    lec_num = lec_info[0].text.strip().replace(' ', '')
                    lec_placement = lec_info[1].text.strip()
                    lec_comp_div = lec_info[2].text.strip()

                    if lec_info[3].find('br') is not None:
                        lec_title, br, lec_note = lec_info[3].contents
                        lec_title = unicode(lec_title).strip()
                        lec_note = unicode(lec_note).strip()
                    else:
                        lec_title = lec_info[3].text.strip()
                        lec_note = ''

                    lec_prof = lec_info[4].text.strip()
                    credit_time = str(lec_info[5].text.strip()).split('(')
                    lec_credit = int(credit_time[0])
                    lec_time = int(credit_time[1][:-1])

                    lec_date_classroom = lec_info[6].text.strip()

                    lec_is_english = True if u'(영강)' in lec_title else False
                    lec_is_relative = False if lec_info[7].text == '' else True
                    lec_is_limit = False if lec_info[8].text == '' else True
                    lec_is_waiting = False if lec_info[9].text == '' else True
                    lec_is_exchange = False if lec_info[10].text == '' else True
                    lec_is_self_attend_check = False if lec_info[11].text == '' else True
                    lec_is_no_supervision = False if lec_info[12].text == '' else True

                    lec_date = None
                    lec_classroom = None
                    if lec_date_classroom != "":
                        lec_date = []
                        try:
                            dc = [m.groupdict() for m in RE_DC.finditer(lec_date_classroom)]
                            if len(dc) == 0:
                                dc = [m.groupdict() for m in RE_DC_DAYONLY.finditer(lec_date_classroom)]
                            
                            if len(dc) != 0:
                                for q in dc:
                                    lec_date.append(q['day'])
                                    if 'classroom' in q:
                                        lec_classroom = q['classroom']
                        
                                lec_date = ','.join(lec_date)
                        except Exception as e:
                            print str(e)
                            lec_date = None
                            lec_classroom = None
                            global_error_list.append([_type, current_col, current_dept, str(e)])

                    lecture, created = Lecture.objects.get_or_create(
                                year=YEAR, semester=SEMESTER, col=current_col, dept=current_dept,
                                number=lec_num, placement=lec_placement, comp_div=lec_comp_div,
                                title=lec_title, professor=lec_prof, credit=lec_credit, time=lec_time,
                                dayAndPeriod=lec_date, classroom=lec_classroom,
                                isEnglish=lec_is_english, isRelative=lec_is_relative,
                                isLimitStudent=lec_is_limit, isWaiting=lec_is_waiting,
                                isExchange=lec_is_exchange,
                                isSelfAttendCheck=lec_is_self_attend_check,
                                isNoSupervision=lec_is_no_supervision,
                                note=lec_note
                             )
                    if not DEBUG and not created:
                        lecture.save()

            except Exception as e:
                err = [_type, current_col, current_dept, str(e), sys.exc_info()[2].tb_lineno]
                print err
                global_error_list.append(err)


def run():
    #lang = KOR, ENG
    index(MAJOR)
    index(ETC, campus=ANAM)
    #index(ETC, SEJONG)
    #index(GRADUATE)

    for error in global_error_list:
        print error

if __name__ == '__main__':
    run()
