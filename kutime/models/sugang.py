from django.db import models


class College(models.Model):
    number = models.CharField(max_length=4)
    name = models.TextField()

    class Meta:
        app_label = 'kutime'


class Department(models.Model):
    col = models.ForeignKey(College)
    
    number = models.CharField(max_length=4)
    name = models.TextField()

    class Meta:
        app_label = 'kutime'

class Lecture(models.Model):
    year = models.IntegerField()
    semester = models.CharField(max_length=2)

    col = models.ForeignKey(College)
    dept = models.ForeignKey(Department)

    number = models.CharField(max_length=7)

    credit = models.IntegerField()
    time = models.IntegerField()

    date = models.TextField()
    classroom = models.TextField()

    isRelative = models.BooleanField(default=True)
    isLimitStudent = models.BooleanField(default=True)
    isWaiting = models.BooleanField(default=False)
    isExchnage = models.BooleanField(default=True)

    class Meta:
        app_label = 'kutime'
