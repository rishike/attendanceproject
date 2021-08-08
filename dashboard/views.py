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
from datetime import datetime, timedelta, timezone

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
        if request.session['typ'] == 'Admin':
            context_data['permission'] = True
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
                not_marked[0].marked_out = NOW
                not_marked[0].save()
                res['msg'] = "Attendance has been marked out successfully for " + res['username']
            elif Attendance.objects.filter(userid_id=user[0].id, marked_out__gte=START_DATE, marked_out__lte=END_DATE):
                res['msg'] = "Attendance has already been marked out successfully for " + res['username']
                return JsonResponse(res, status=200)
            else:
                res['msg'] = res['username'] + " need to mark in first."
        return JsonResponse(res, status=200)


class TrainingView(View):
    template_name = "dashboard/training.html"

    def get(self, request):
        context_data = check_session(request)
        if context_data:
            if context_data.get('permission'):
                return render(request, template_name=self.template_name, context=context_data)
            else:
                return render(request, template_name='403.html')
        else:
            return redirect('accounts:login')

    def post(self, request):
        res = Training()
        if res.get('status') == 11:
            res['msg'] = "Image processing compelete"
            return JsonResponse(res, status=200)
        elif res.get('status') == 00:
            res['msg'] = "500 internal server error"
            return JsonResponse(res, status=200)


class MarkAttendanceView(View):
    def get(self, request):
        res = Recognizer(status='in')
        if res.get('status') == 11:
            user = Accounts.objects.filter(username=res['username'], active=1)
            if not user:
                res['msg'] = "sorry that users does not exist."
                return JsonResponse(res, status=200)

            if Attendance.objects.filter(userid_id=user[0].id, marked_at__gte=START_DATE, marked_at__lte=END_DATE):
                res['msg'] = "Attendance has already been marked successfully for " + res['username']
                return JsonResponse(res, status=200)

            attd = Attendance.objects.create(userid=user[0], marked_at=NOW)
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


class AllAttendanceView(View):
    template_name = "dashboard/all_attendance.html"

    def get(self, request):
        context_data = check_session(request)
        if context_data.get('permission'):
            final_obj = {}
            all_usr_obj = Accounts.objects.all()
            context_data['total_user'] = all_usr_obj.count()
            all_name_join = {_.name: [_.created_at.date(), []] for _ in all_usr_obj}
            all_diff = {k: NOW.date() - v[0] for k, v in all_name_join.items()}
            [all_name_join[_.userid.name][1].append([_.created_at.date(), _.marked_at, _.marked_out]) for _ in Attendance.objects.all() ]

            for k, v in all_name_join.items():

                final_obj[k] = {}
                for _ in range(all_diff[k].days):
                    day = v[0] + timedelta(_)
                    final_obj[k][_] = {}
                    final_obj[k][_]['day'] = day
                    final_obj[k][_]['marked_at'] = "-"
                    final_obj[k][_]['marked_out'] = "-"
                    final_obj[k][_]['status'] = 'Absent'

                    for idx in v[1]:
                        if day == idx[0]:
                            final_obj[k][_]['day'] = day
                            final_obj[k][_]['marked_at'] = idx[1]
                            final_obj[k][_]['marked_out'] = idx[2]
                            final_obj[k][_]['status'] = 'Present'

            context_data['final_obj'] = final_obj
            return render(request, template_name=self.template_name, context=context_data)
        return render(request, template_name='403.html')


class AttendanceListView(View):
    template_name = "dashboard/attendance.html"

    def get(self, request, username):
        context_data = check_session(request)
        user_obj = get_object_or_404(Accounts, username=username)

        if context_data.get('permission'):
            att_obj = Attendance.objects.filter(userid=user_obj.id)
        elif context_data['username'] == username:
            att_obj = Attendance.objects.filter(userid=user_obj.id)
        else:
            return render(request, template_name='403.html')

        present_data = {_.marked_at.date(): [_.marked_at, _.marked_out] for _ in att_obj}

        if not context_data:
            return redirect('accounts:login')
        context_data['profile_username'] = user_obj.name
        context_data['joined_on'] = user_obj.created_at
        diff = NOW.date() - user_obj.created_at.date()
        context_data['total_attendance'] = diff.days
        context_data['total_present'] = len(att_obj)
        context_data['total_absent'] = diff.days - len(att_obj)
        context_data['att_obj'] = att_obj
        context_data['full_name'] = user_obj.name
        atte_dict = {}

        for _ in range(diff.days):
            atte_dict[_] = {}
            day = user_obj.created_at.date() + timedelta(_)
            atte_dict[_]['day'] = day
            atte_dict[_]['marked_at'] = "-"
            atte_dict[_]['marked_out'] = "-"
            atte_dict[_]['status'] = 'Absent'

            if present_data.get(day):
                atte_dict[_]['day'] = day
                atte_dict[_]['marked_at'] = present_data[day][0]
                atte_dict[_]['marked_out'] = present_data[day][1]
                atte_dict[_]['status'] = 'Present'

        context_data['atte_obj'] = atte_dict
        context_data['name'] = user_obj.name

        return render(request, self.template_name, context_data)


class DashboardView(View):
    template_name = "dashboard/dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

    def get(self, request):
        context_data = check_session(request)
        if context_data:
            context_data['userid'] = Accounts.objects.get(username=context_data['username'])
            return render(request, self.template_name, context_data)
        else:
            return redirect('accounts:login')
