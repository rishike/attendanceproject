from django.shortcuts import render, redirect
from django.views.generic.base import TemplateView
from django.views import View
from django.http import HttpResponse, JsonResponse
from utils.recognize import Recognizer
from accounts.models import Accounts
from .models import Attendance
from django.views.decorators.http import require_http_methods
# Create your views here.


@require_http_methods(["POST"])
def CheckEmail(request):
    if request.POST.get('email'):
        user_obj = Accounts.objects.filter(email=request.POST['email'])
        if user_obj:
            return JsonResponse({
                'username': user_obj[0].username,
                'status': 200
            }, status=200)
        else:
            return JsonResponse({
                'msg': "Email does not exist in our records",
                'status': 400
            }, status=200)
    else:
        return JsonResponse({
            'msg': "Email does not exist in our records",
            'status': 400
        }, status=200)


class MarkAttendanceView(View):

    def get(self, request):
        res = dict()
        # if request.POST.get('username'):
        res = Recognizer(username='rishi')
        return JsonResponse(res, status=200)


class FirstPageView(View):
    template_name = "dashboard/first_page.html"

    def get(self, request):
        context_data = {}
        return render(request, self.template_name, context_data)


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