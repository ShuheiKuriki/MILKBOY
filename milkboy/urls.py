from django.urls import path
from . import views

app_name = 'milkboy'

urlpatterns = [
    path('', views.index, name='index'),
    path('theme', views.theme),
    path('genre', views.genre),
    path('tweet', views.tweet)
]