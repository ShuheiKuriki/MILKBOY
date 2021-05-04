from django.shortcuts import render
from milkboy.views import GENRES
from django.views.generic import TemplateView


def index(request):
    return render(request, 'index.html', {'genres': GENRES})
# Create your views here.
