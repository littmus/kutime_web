#-*- coding:utf-8 -*-
from django.db import models


class College(models.Model):
    number = models.CharField(max_length=4)
    name = models.CharField(max_length=50)

    CHOICES_CAMPUS = (
        ('A', u'안암'),
        ('S', u'세종'),
        ('G', u'대학원'),
        ('E', u'기타'),
    )
    campus = models.CharField(max_length=1, choices=CHOICES_CAMPUS, null=True)

    CHOICES_TYPE = (
        ('M', u'학부 전공'),
        ('E', u'학부 교양/교직/기타'),
        ('G', u'대학원 전공'),
    )
    type = models.CharField(max_length=1, choices=CHOICES_TYPE)

    class Meta:
        app_label = 'kutime'
        unique_together = (('number', 'campus'))

    def __unicode__(self):
        return self.name


class Department(models.Model):
    col = models.ForeignKey(College)
    
    number = models.CharField(max_length=4)
    name = models.CharField(max_length=50)

    class Meta:
        app_label = 'kutime'

    def __unicode__(self):
        return u'%s - %s' % (self.col.name, self.name)

class DayAndPeriod(object):
    day = None
    period_start = None
    period_end = None

    def __init__(self, dayAndPeriod=None):
        if dayAndPeriod is not None:
            try:
                day, period = dayAndPeriod.split('(')
                self.day = day
                
                period = period[:-1]
                if '-' in period:
                    self.period_start, self.period_end = map(int, period.split('-'))
                else:
                    self.period_start = self.period_end = int(period)
            except Exception as e:
                print str(e)
                self.day = None
                self.period_start = None
                self.period_end = None
    
    def __unicode__(self):
        if self.period_start == self.period_end:
            return u'%s(%d)' % (self.day, self.period_start)
        else:
            return u'%s(%d-%d)' % (self.day, self.period_start, self.period_end)
    

class DayAndPeriodField(models.CharField):
    description = "A field for day and period pair"
    __metaclass__ = models.SubfieldBase

    def __init__(self, *args, **kwargs):
        self.name  = "DayAndPeriodField"

        super(DayAndPeriodField, self).__init__(*args, **kwargs)

    def to_python(self, value):
        if value is None:
            return ''
        if isinstance(value, DayAndPeriod):
            return value
        if isinstance(value, list):
            return ','.join([unicode(v) for v in value])
        
        return value

    def get_db_prep_value(self, value, connection=None, prepared=False):
        if isinstance(value, basestring):
            return value
        elif isinstance(value, list):
            return ','.join([unicode(v) for v in value])
        elif isinstance(value, DayAndPeriod):
            return unicode(value)

    def value_to_string(self, obj):
        value = self._get_val_from_obj(obj)
        return self.get_db_prep_value(value)


class Lecture(models.Model):
    year = models.IntegerField()

    CHOICES_SEMESTER = (
        ('1R', u'1학기'),
        ('1S', u'여름학기'),
        ('2R', u'2학기'),
        ('2W', u'겨울학기'),
        ('SC', u'국제하계대학'),
    )
    semester = models.CharField(max_length=2, choices=CHOICES_SEMESTER)

    col = models.ForeignKey(College)
    dept = models.ForeignKey(Department)

    number = models.CharField(max_length=7)
    placement = models.CharField(max_length=2)
    comp_div = models.CharField(max_length=50)
    title = models.CharField(max_length=200)
    professor = models.CharField(max_length=200)

    credit = models.IntegerField()
    time = models.IntegerField()

    dayAndPeriod = DayAndPeriodField(max_length=500, null=True)
    classroom = models.CharField(max_length=50, null=True)

    isEnglish = models.BooleanField(default=False)
    isRelative = models.BooleanField(default=True)
    isLimitStudent = models.BooleanField(default=True)
    isWaiting = models.BooleanField(default=True)
    isExchange = models.BooleanField(default=True)
    isSelfAttendCheck = models.BooleanField(default=False)
    isNoSupervision = models.BooleanField(default=False)

    note = models.TextField(null=True)

    class Meta:
        app_label = 'kutime'
        unique_together = (('number', 'placement'))
    
    def link_lecture_plan(self):
        url = 'http://infodepot.korea.ac.kr/lecture1/lecsubjectPlanView.jsp?%(year)d&term=%(term)s&grad_cd=%(cols)s&dept_cd=%(dept)s&cour_cd=%(lec_num)s&cour_cls=%(placement)s' % {
            'year': self.year,
            'term': self.semester,
            'cols': self.col.number,
            'dept': self.dept.number,
            'lec_num': self.number,
            'placement': self.placement,
        }

        return url

    def __unicode__(self):
        return u'%s - %s' % (self.title, self.professor)

