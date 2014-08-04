# -*- coding:utf-8 -*-
import os
import time
import re
import requests
from bs4 import BeautifulSoup as bs

os.environ['DJANGO_SETTINGS_MODULE'] = 'kutime.settings'

from kutime.models.kutime import *

URL_MAJOR = 'http://sugang.korea.ac.kr/lecture/LecMajorSub.jsp'
URL_ETC = 'http://sugang.korea.ac.kr/lecture/LecEtcSub.jsp'
URL_GRADUATE = 'http://sugang.korea.ac.kr/lecture/LecGradMajorSub.jsp'
URL_DEPT_MAJOR = 'http://sugang.korea.ac.kr/lecture/LecDeptPopup.jsp?frm=frm_ms&colcd=%(colcd)s&deptcd=%(deptcd)s&dept=%(dept)s&year=%(year)s&term=%(term)s'
URL_DEPT_ETC = 'http://sugang.korea.ac.kr/lecture/LecDeptPopup.jsp?frm=frm_ets&colcd=%(colcd)s&deptcd=%(deptcd)s&dept=%(dept)s'

RE_DEPT = re.compile(u'el.value ="(?P<num>\d{2,4})";\r\n            el.text = "(?P<name>[\uac00-\ud7a3\w ·]+)";', re.UNICODE)
RE_DC = re.compile(u'(?P<day>[\uac00-\ud7a3]{1}\([\d-]+\)) (?P<classroom>[\uac00-\ud7a3\w\d\- ]*(?=[\uac00-\ud7a3\w\d\- ])\d\S)', re.UNICODE)
RE_DC_DAYONLY = re.compile(u'(?P<day>[\uac00-\ud7a3]{1}\([\d-]+\))', re.UNICODE)
YEAR = 2014
SEMESTER = '2R'

MAJOR = 'M'
ETC = 'E'
GRADUATE = 'G'

def index(_type):
    if _type == MAJOR:
        URL = URL_MAJOR
        URL_DEPT = URL_DEPT_MAJOR
        TABLE_INDEX = 5
    elif _type == ETC:
        URL = URL_ETC
        URL_DEPT = URL_DEPT_ETC
        TABLE_INDEX = 7
    elif _type == GRADUATE:
        URL = URL_GRADUATE
        TABLE_INDEX = -1

    error_list = []
    r = requests.get(URL)
    soup = bs(r.text)
    cols = soup.find('select', attrs={'name':'col'})

    for col in cols.find_all('option'): 
        if 'red' in col:
            continue
                
        number = col['value']
        name = col.text.strip()
        
        current_col = College(number=number, name=name, type=_type)
        current_col.save()

        print name

        if _type == MAJOR:
            dept_url = URL_DEPT % {'colcd':number, 'deptcd':'', 'dept':'dept', 'year':YEAR, 'term':SEMESTER}
        elif _type == ETC:
            dept_url = URL_DEPT % {'colcd':number, 'deptcd':'', 'dept':'dept', 'campus':'1'}
        elif _type == GRADUATE:
            print ''

        r = requests.get(dept_url)
        
        _soup = bs(r.text)
        depts = _soup.find('script')
        m = [m.groupdict() for m in RE_DEPT.finditer(depts.text)]
        for dept in m:
            if 'red' in dept:
                continue

            dept_num = str(dept['num'])
            dept_name = dept['name'].strip()
            
            print dept_name

            current_dept = Department(col=current_col, number=dept_num, name=dept_name, type=_type)
            current_dept.save()
            
            params = {
                'yy': YEAR,
                'tm': SEMESTER,
                'col': number,
                'dept': dept_num,
            }

            if _type == ETC:
                params['campus'] = '1'

            r = requests.post(URL, params=params)
            lec_soup = bs(r.text)
            table = lec_soup.find_all('table')[TABLE_INDEX]
            if u'검색결과가' in table.text:
                continue
            
            try:
                for lec_row in table.find_all('tr')[3::2]:
                    lec_info = lec_row.find_all('td')[::2]
                    
                    if _type == MAJOR:
                        lec_campus = 'A' if lec_info[0].text == u'안암' else 'S'
                        lec_num = lec_info[1].text.strip()
                        lec_placement = lec_info[2].text.strip()
                        lec_comp_div = lec_info[3].text.strip()
                        if 'br' in lec_info[4]:
                            print lec_info[4]
                            raw_input()
                        lec_title = lec_info[4].text.strip()
                        lec_prof = lec_info[5].text.strip()
                        credit_time = str(lec_info[6].text.strip()).split('(')
                        lec_credit = int(credit_time[0])
                        lec_time = int(credit_time[1][-2])

                        lec_date_classroom = lec_info[7].text.strip()

                        lec_is_english = True if u'(영강)' in lec_title else False
                        lec_is_relative = False if lec_info[8].text == '' else True
                        lec_is_limit = False if lec_info[9].text == '' else True
                        lec_is_waiting = False if lec_info[10].text == '' else True
                        lec_is_exchange = False if lec_info[11].text == '' else True
                    elif _type == ETC:
                        lec_campus = 'A'
                        lec_num = lec_info[0].text.strip()
                        lec_placement = lec_info[1].text.strip()
                        lec_comp_div = ''
                        if 'br' in lec_info[2]:
                            print lec_info[2]
                            raw_input()
                        lec_title = lec_info[2].text.strip()
                        lec_prof = lec_info[3].text.strip()
                        credit_time = str(lec_info[4].text.strip()).split('(')
                        lec_credit = int(credit_time[0])
                        lec_time = int(credit_time[1][-2])

                        lec_date_classroom = lec_info[5].text.strip()

                        lec_is_english = True if u'(영강)' in lec_title else False
                        lec_is_relative = False if lec_info[6].text == '' else True
                        lec_is_limit = False if lec_info[7].text == '' else True
                        lec_is_waiting = False if lec_info[8].text == '' else True
                        lec_is_exchange = False if lec_info[9].text == '' else True

                    lec_date = None
                    lec_classroom = None
                    if lec_date_classroom != '':
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

                    print lec_date, lec_classroom

                    lec_note = ''

                    lecture = Lecture(
                                year=YEAR, semester=SEMESTER, col=current_col, dept=current_dept,
                                campus=lec_campus, number=lec_num, placement=lec_placement, comp_div=lec_comp_div,
                                title=lec_title, professor=lec_prof, credit=lec_credit, time=lec_time,
                                dayAndPeriod=lec_date, classroom=lec_classroom,
                                isEnglish=lec_is_english, isRelative=lec_is_relative,
                                isLimitStudent=lec_is_limit, isWaiting=lec_is_waiting,
                                isExchange=lec_is_exchange,
                                note=lec_note
                             )
                    lecture.save()
            except Exception as e:
                print str(e)
                error_list.append([current_col, current_dept, str(e)])

    for error in error_list:
        print error

def run():
    index(MAJOR)
    index(ETC)
    #index(GRADUATE)

if __name__ == '__main__':
    run()
