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
RE_DEPT = re.compile(u'el.value ="(?P<num>\d{2,4})";\r\n            el.text = "(?P<name>[\uac00-\ud7a3\w ]+)";', re.UNICODE)

YEAR = 2014
SEMESTER = '2R'

def index(URL):
    r = requests.get(URL)
    soup = bs(r.text)
    cols = soup.find('select', attrs={'name':'col'})
    for col in cols.find_all('option'):
        number = col['value']
        name = col.text.rstrip()
        
        current_col = College(number=number, name=name)
        current_col.save()

        print name

        dept_url = URL_DEPT % {'colcd':number, 'deptcd':'', 'dept':'dept', 'year':'2014', 'term':'2R'}
        r = requests.get(dept_url)
        
        _soup = bs(r.text)
        depts = _soup.find('script')
        m = [m.groupdict() for m in RE_DEPT.finditer(depts.text)]
        for dept in m:
            dept_num = str(dept['num'])
            dept_name = dept['name'].rstrip()
            
            print dept_name

            current_dept = Department(col=current_col, number=dept_num, name=dept_name)
            current_dept.save()

            params = {
                'yy': '2014',
                'tm': '2R',
                'col': number,
                'dept': dept_num,
            }

            r = requests.post(URL, params=params)
            lec_soup = bs(r.text)
            table = lec_soup.find_all('table')[5]
            if u'검색결과가' in table.text:
                continue

            for lec_row in table.find_all('tr')[3::2]:
                lec_info = lec_row.find_all('td')[::2]
                
                campus = lec_info[0].text
                lec_num = lec_info[1].text
                lec_placement = lec_info[2].text
                lec_comp_div = lec_info[3].text
                lec_title = lec_info[4].text.lstrip().rstrip()
                lec_prof = lec_info[5].text
                credit_time = str(lec_info[6].text).split('(')
                lec_credit = int(credit_time[0])
                lec_time = int(credit_time[1][-2])

                lec_date_classroom = lec_info[7].strings
                lec_date = []
                lec_classroom = None
                try:
                    for date_classroom in lec_date_classroom:
                        date, classroom = date_classroom.split(' ', 1)                
                        lec_date.append(date)
                        lec_classroom = classroom
                
                    lec_date = ','.join(lec_date)
                except ValueError:
                    lec_date = None
                    lec_classroom = None

                print lec_date
                print lec_classroom 

                lecture = Lecture(
                            year=YEAR, semester=SEMESTER, col=current_col, dept=current_dept,
                            campus='A', number=lec_num, placement=lec_placement, comp_div=lec_comp_div,
                            title=lec_title, professor=lec_prof, credit=lec_credit, time=lec_time,
                            dayAndPeriod=lec_date, classroom=lec_classroom
                         )
                lecture.save()
#            raw_input() 

def run():
    index(URL_MAJOR)
#    index(URL_ETC)
#    index(URL_GRADUATE)

if __name__ == '__main__':
    run()
