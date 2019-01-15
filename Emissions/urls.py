from django.urls import path
from . import views # import views.py from the current dir

urlpatterns = [
    path("", views.index)
]