from django.urls import path
from .views import DashboardView, MarkAttendanceView, TrainingView, MarkAttendanceOutView, AttendanceListView,\
    AllAttendanceView

app_name = 'dashboard'

urlpatterns = [
    path('dashboard/', DashboardView.as_view(), name='home'),
    path('markattendance/', MarkAttendanceView.as_view(), name='mark-attendance'),
    path('markoutattendance/', MarkAttendanceOutView.as_view(), name='mark-out-attendance'),
    path('training/all/', TrainingView.as_view(), name="training"),
    path('attendance/<str:username>/', AttendanceListView.as_view(), name="attendance-history"),
    path('attendance/show/all/', AllAttendanceView.as_view(), name="all-attendance-history"),
]
