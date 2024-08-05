from django.contrib import admin
from django.urls import path, include
from home import views as v
urlpatterns = [
    path("", v.HomePageView.as_view(), name="home"),
]
