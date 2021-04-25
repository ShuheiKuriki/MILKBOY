from django.urls import path
from . import views

app_name = 'milkboy'

urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('stage', views.stage)
]