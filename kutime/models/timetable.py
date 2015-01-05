# -*- coding: utf-8 -*-
from django.db import models
from django.contrib.postgres.fields import ArrayField

from kutime.models.kutime import Lecture


class Timetable(models.Model):
    # just contain Lecture IDs?
    pass
