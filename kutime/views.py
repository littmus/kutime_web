from django.shortcuts import render

from kutime.models.kutime import College

def index(request):
    list_cols = College.objects.all()

    return render(
        request,
        'index.html',
        {
            'cols': list_cols,
        }
    )

