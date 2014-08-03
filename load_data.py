# -*- coding:utf-8 -*-
import os
import re
import requests
from bs4 import BeautifulSoup as bs

os.environ['DJANGO_SETTINGS_MODULE'] = 'kutime.settings'

from kutime.models.kutime import *

URL_MAJOR = 'http://sugang.korea.ac.kr/lecture/LecMajorSub.jsp'
URL_ETC = 'http://sugang.korea.ac.kr/lecture/LecEtcSub.jsp'
URL_GRADUATE = 'http://sugang.korea.ac.kr/lecture/LecGradMajorSub.jsp'
URL_DEPT = 'http://sugang.korea.ac.kr/lecture/LecDeptPopup.jsp?frm=frm_ms&colcd=%(colcd)s&deptcd=%(deptcd)s&dept=%(dept)s&year=%(year)s&term=%(term)s'
URL_DEPT_ETC = 'http://sugang.korea.ac.kr/lecture/LecDeptPopup.jsp?frm=frm_ets&colcd=%(colcd)s&deptcd=%(deptcd)s&dept=%(dept)s'

RE_DEPT = re.compile(u'el.value ="(?P<num>\d{2,4})";\r\n            el.text = "(?P<name>[\uac00-\ud7a3\w ·]+)";', re.UNICODE)
RE_DC = re.compile(u'(?P<day>[\uac00-\ud7a3]{1}\([\d-]+\)) (?P<classroom>[\uac00-\ud7a3\w\d\- ]+(?=[\uac00-\ud7a3\w\d\- ])\d\S)', re.UNICODE)
YEAR = 2014
SEMESTER = '2R'

def index(URL):
    error_list = []
    r = requests.get(URL)
    soup = bs(r.text)
    cols = soup.find('select', attrs={'name':'col'})

    for col in cols.find_all('option'): 
        if 'red' in col:    
            continue
                
        number = col['value']
        name = col.text.strip()
        
        current_col = College(number=number, name=name, type='M')
        #current_col.save()

        print name
        dept_url = URL_DEPT % {'colcd':number, 'deptcd':'', 'dept':'dept', 'year':YEAR, 'term':SEMESTER}
        r = requests.get(dept_url)
        
        _soup = bs(r.text)
        depts = _soup.find('script')
        m = [m.groupdict() for m in RE_DEPT.finditer(depts.text)]
        for dept in m:
            dept_num = str(dept['num'])
            dept_name = dept['name'].strip()
            
            print dept_name

            current_dept = Department(col=current_col, number=dept_num, name=dept_name, type='M')
            #current_dept.save()
            
            params = {
                'yy': YEAR,
                'tm': SEMESTER,
                'col': number,
                'dept': dept_num,
            }

            r = requests.post(URL, params=params)
            lec_soup = bs(r.text)
            table = lec_soup.find_all('table')[5]
            if u'검색결과가' in table.text:
                continue
            
            try:
                for lec_row in table.find_all('tr')[3::2]:
                    lec_info = lec_row.find_all('td')[::2]
                    
                    campus = lec_info[0].text
                    lec_num = lec_info[1].text
                    lec_placement = lec_info[2].text
                    lec_comp_div = lec_info[3].text
                    lec_title = lec_info[4].text.strip()
                    lec_prof = lec_info[5].text
                    credit_time = str(lec_info[6].text).split('(')
                    lec_credit = int(credit_time[0])
                    lec_time = int(credit_time[1][-2])

                    lec_date_classroom = lec_info[7].text.strip()
                    lec_date = []
                    lec_classroom = None
                    try:
                        print lec_date_classroom
                        dc = [m.groupdict() for m in RE_DC.finditer(lec_date_classroom)]
                        for q in dc:
                            lec_date.append(q['day'])
                            lec_classroom = q['classroom']
                    
                        lec_date = ','.join(lec_date)
                    except ValueError as e:
                        print str(e)
                        lec_date = None
                        lec_classroom = None
                    
                    lec_is_english = True if u'(영강)' in lec_title else False
                    lec_is_relative = False if lec_info[8].text == '' else True
                    lec_is_limit = False if lec_info[9].text == '' else True
                    lec_is_waiting = False if lec_info[10].text == '' else True
                    lec_is_exchange = False if lec_info[11].text == '' else True

                    lecture = Lecture(
                                year=YEAR, semester=SEMESTER, col=current_col, dept=current_dept,
                                campus='A', number=lec_num, placement=lec_placement, comp_div=lec_comp_div,
                                title=lec_title, professor=lec_prof, credit=lec_credit, time=lec_time,
                                dayAndPeriod=lec_date, classroom=lec_classroom,
                                isEnglish=lec_is_english, isRelative=lec_is_relative,
                                isLimitStudent=lec_is_limit, isWaiting=lec_is_waiting,
                                isExchange=lec_is_exchange
                             )
                    #lecture.save()
            except Exception as e:
                print str(e)
                error_list.append([current_col, current_dept, str(e)])

    for error in error_list:
        print error


def index_etc(URL):
    error_list = []
    r = requests.get(URL)
    soup = bs(r.text)
    cols = soup.find('select', attrs={'name':'col'})

    for col in cols.find_all('option'): 
        if 'red' in col:    
            continue
                
        number = col['value']
        name = col.text.strip()
        
        current_col = College(number=number, name=name, type='E')
        current_col.save()

        print name
        dept_url = URL_DEPT_ETC % {'colcd':number, 'deptcd':'', 'dept':'dept', 'campus':'1'}
        r = requests.get(dept_url)
        
        _soup = bs(r.text)
        depts = _soup.find('script')
        m = [m.groupdict() for m in RE_DEPT.finditer(depts.text)]
        for dept in m:
            dept_num = str(dept['num'])
            dept_name = dept['name'].strip()
            
            print dept_name

            current_dept = Department(col=current_col, number=dept_num, name=dept_name, type='E')
            current_dept.save()
            
            params = {
                'yy': YEAR,
                'tm': SEMESTER,
                'col': number,
                'dept': dept_num,
                'campus': '1',
            }

            r = requests.post(URL, params=params)
            lec_soup = bs(r.text)
            table = lec_soup.find_all('table')[7]
            if u'검색결과가' in table.text:
                continue
            
            try:
                for lec_row in table.find_all('tr')[3::2]:
                    lec_info = lec_row.find_all('td')[::2]
                    
                    campus = 'A'
                    lec_num = lec_info[0].text
                    lec_placement = lec_info[1].text
                    lec_comp_div = ''
                    lec_title = lec_info[2].text.strip()
                    lec_prof = lec_info[3].text
                    credit_time = str(lec_info[4].text).split('(')
                    lec_credit = int(credit_time[0])
                    lec_time = int(credit_time[1][-2])

                    lec_date_classroom = lec_info[5].strings
                    lec_date = []
                    lec_classroom = None
                    try:
                        for date_classroom in lec_date_classroom:
                            date, classroom = date_classroom.split(' ', 1)                
                            lec_date.append(date)
                            lec_classroom = classroom
                    
                        lec_date = ','.join(lec_date)
                    except ValueError as e:
                        lec_date = None
                        lec_classroom = None
                    
                    lec_is_english = True if u'(영강)' in lec_title else False
                    lec_is_relative = False if lec_info[6].text == '' else True
                    lec_is_limit = False if lec_info[7].text == '' else True
                    lec_is_waiting = False if lec_info[8].text == '' else True
                    lec_is_exchange = False if lec_info[9].text == '' else True

                    lecture = Lecture(
                                year=YEAR, semester=SEMESTER, col=current_col, dept=current_dept,
                                campus='A', number=lec_num, placement=lec_placement, comp_div=lec_comp_div,
                                title=lec_title, professor=lec_prof, credit=lec_credit, time=lec_time,
                                dayAndPeriod=lec_date, classroom=lec_classroom,
                                isEnglish=lec_is_english, isRelative=lec_is_relative,
                                isLimitStudent=lec_is_limit, isWaiting=lec_is_waiting,
                                isExchange=lec_is_exchange
                             )
                    lecture.save()
            except Exception as e:
                error_list.append([current_col, current_dept, str(e)])

    for error in error_list:
        print error


def run():
    index(URL_MAJOR)
#    index_etc(URL_ETC)
#    index(URL_GRADUATE)

if __name__ == '__main__':
    run()
