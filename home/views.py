from django.shortcuts import render, HttpResponseRedirect, HttpResponse
from django.views.generic import View


# Create your views here.
class HomePageView(View):
    def get(self, request):
        return HttpResponse("<h1><a href='/admin'>Login</a></h1>")
