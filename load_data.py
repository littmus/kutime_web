#-*- coding:utf-8 -*-
import os
import re
import requests
from bs4 import BeautifulSoup as bs

os.environ['DJANGO_SETTINGS_MODULE'] = 'kutime.settings'

from kutime.models.sugang import *

URL_MAJOR = 'http://sugang.korea.ac.kr/lecture/LecMajorSub.jsp'
URL_ETC = 'http://sugang.korea.ac.kr/lecture/LecEtcSub.jsp'
URL_GRADUATE = 'http://sugang.korea.ac.kr/lecture/LecGradMajorSub.jsp'
URL_DEPT = 'http://sugang.korea.ac.kr/lecture/LecDeptPopup.jsp?frm=frm_ms&colcd=%(colcd)s&deptcd=%(deptcd)s&dept=%(dept)s&year=%(year)s&term=%(term)s'
#RE_DEPT = re.compile(u'([\uac00-\ud7a3]+)', re.UNICODE)
RE_DEPT = re.compile(u'el.value ="(?P<num>\d{2,4})";\r\n            el.text = "(?P<name>[\uac00-\ud7a3\w ]+)";', re.UNICODE)


def index(URL):
    r = requests.get(URL)
    soup = bs(r.text)
    cols = soup.find('select', attrs={'name':'col'})
    for col in cols.find_all('option'):
        number = col['value']
        name = col.text.rstrip()
        
        current_col = College(number=number, name=name)
        current_col.save()

        print number, name

        dept_url = URL_DEPT % {'colcd':number, 'deptcd':'', 'dept':'dept', 'year':'2014', 'term':'2R'}
        r = requests.get(dept_url)
        
        _soup = bs(r.text)
        depts = _soup.find('script')
        m = [m.groupdict() for m in RE_DEPT.finditer(depts.text)]
        for dept in m:
            dept_num = str(dept['num'])
            dept_name = dept['name'].rstrip()

            current_dept = Department(col=current_col, number=dept_num, name=dept_name)
            current_dept.save()
"""
            params = {
                'yy': '2014',
                'tm': '2R',
                'col': number,
                'dept': dept_num,
            }

            r = requests.post(URL, params=params)
            lec_soup = bs(r.text)
            table = lec_soup.find_all('table')[5]
            for lec_row in table.find_all('tr')[1::2]:
                lec_info = lec_row.find_all('td')[::2]

                campus = lec_info[0].text
                lec_num = lec_info[1].text
                lec_title = lec_info[4].text
                lec_prof = lec_info[5].text
                print lec_title, lec_prof

            raw_input() 
"""

def run():
    index(URL_MAJOR)
#    index(URL_ETC)
#    index(URL_GRADUATE)

if __name__ == '__main__':
    run()
