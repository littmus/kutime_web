# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.apps import AppConfig

import watson

class KutimeConfig(AppConfig):
    name = 'kutime'

    def ready(self):
        Lecture = self.get_model('Lecture')
        watson.register(Lecture)

