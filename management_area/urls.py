from django.urls import path
from . import views

app_name = 'management_area'
urlpatterns = [
    path('entry_detail/<int:entry_id>/',views.entry_detail, name='entry_detail')
]