from django.shortcuts import render, redirect
from django.views.generic.base import TemplateView
from django.views import View
from django.http import HttpResponse, JsonResponse, response
from utils.recognize import Recognizer
from utils.training import Training
from accounts.models import Accounts
from .models import Attendance
from django.views.decorators.http import require_http_methods
from django.shortcuts import get_object_or_404
from django.conf import settings
import os
import pathlib
from datetime import datetime

NOW = datetime.now()
START_DATE = datetime(NOW.year, NOW.month, NOW.day, hour=00, minute=00, second=00)
END_DATE = datetime(NOW.year, NOW.month, NOW.day, hour=23, minute=59, second=59)

# Create your views here.
@require_http_methods(["GET", "POST"])
def fetch_processing_image(request, param):
    if param in request.session:
        return JsonResponse({
            param: request.session[param]
        }, status=200)

    return HttpResponse("fail")


def check_session(request):
    if 'username' in request.session and 'typ' in request.session and 'name' in request.session:
        context_data = dict()
        context_data['username'], context_data['typ'], context_data['name'] = request.session['username'], \
                                                                              request.session['typ'], request.session[
                                                                                  'name']
        return context_data
    return False


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


class MarkAttendanceOutView(View):

    def get(self, request):
        res = Recognizer(status='out')
        if res.get('status') == 11:
            user = Accounts.objects.filter(username=res['username'])
            not_marked = Attendance.objects.filter(userid_id=user[0].id, marked_at__gte=START_DATE, marked_at__lte=END_DATE, marked_out__isnull=True)
            if not_marked:
                print('not_marked')
                not_marked[0].marked_out = NOW
                not_marked[0].save()
                res['msg'] = "Attendance has been marked out successfully for " + res['username']
            elif Attendance.objects.filter(userid_id=user[0].id, marked_out__gte=START_DATE, marked_out__lte=END_DATE):
                res['msg'] = "Attendance has already been marked out successfully for " + res['username']
                return JsonResponse(res, status=200)
            else:
                res['msg'] = res['username'] + " has not exist in our record."
        return JsonResponse(res, status=200)


class TrainingView(View):
    template_name = "dashboard/training.html"

    def get(self, request, username):
        context_data = check_session(request)
        if context_data:
            profile_obj = get_object_or_404(Accounts, username=username)
            pth = os.path.join(settings.MEDIA_ROOT, profile_obj.username)
            filenames = []
            for path, subdirs, files in os.walk(pth):
                for name in files:
                    if pathlib.Path(name).suffix in ['.jpg', '.jpeg', '.png']:
                        filenames.append(name)
            context_data['filenames'] = filenames
            return render(request, template_name=self.template_name, context=context_data)
        else:
            return redirect('accounts:login')

    def post(self, request, username):
        res = Training(request, username)
        return JsonResponse({
            'msg': 'success',
            'status': "200"
        }, status=200)




class MarkAttendanceView(View):
    def get(self, request):
        res = Recognizer(status='in')
        if res.get('status') == 11:
            user = Accounts.objects.filter(username=res['username'])

            if Attendance.objects.filter(userid_id=user[0].id, marked_at__gte=START_DATE, marked_at__lte=END_DATE):
                res['msg'] = "Attendance has already been marked successfully for " + res['username']
                return JsonResponse(res, status=200)

            attd = Attendance.objects.create(userid=user[0], marked_in=NOW)
            attd.save()
            res['msg'] = "Attendance has been marked successfully for " + res['username']
        return JsonResponse(res, status=200)


class FirstPageView(View):
    template_name = "dashboard/first_page.html"

    def get(self, request):
        context_data = check_session(request)
        if not context_data:
            return render(request, self.template_name, {})
        else:
            return redirect('dashboard:home')


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
