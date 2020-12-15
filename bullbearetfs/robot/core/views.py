from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse
from bullbearetfs.forms import contactForm

# Import Views
from django.views.generic import ListView, DetailView,View,TemplateView, FormView
from django.views.generic import CreateView, UpdateView,DeleteView
