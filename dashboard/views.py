from django.shortcuts import render, redirect
from django.views.generic.base import TemplateView
from django.views import View
from django.http import HttpResponse

# Create your views here.


class DashboardView(View):
    template_name = "dashboard/dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

    def get(self, request):
        context_data = {}
        if 'username' in request.session and 'typ' in request.session and 'name' in request.session:
            context_data['username'] = request.session['username']
            context_data['typ'] = request.session['typ']
            context_data['name'] = request.session['name']

            return render(request, self.template_name, context_data)
        else:
            return redirect('accounts:login')