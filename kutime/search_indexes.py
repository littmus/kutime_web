from haystack import indexes
from kutime.models.kutime import *


class LectureIndex(indexes.SearchIndex, indexes.Indexable):
    number = indexes.CharField(document=True)

    def get_model(self):
        return Lecture

    def index_queryset(self, using=None):
        return self.get_model().objects.all()
