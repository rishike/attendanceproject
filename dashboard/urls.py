from django.urls import path
from .views import DashboardView, MarkAttendanceView, TrainingView, MarkAttendanceOutView, AttendanceList

app_name = 'dashboard'

urlpatterns = [
    path('dashboard/', DashboardView.as_view(), name='home'),
    path('markattendance/', MarkAttendanceView.as_view(), name='mark-attendance'),
    path('markoutattendance/', MarkAttendanceOutView.as_view(), name='mark-out-attendance'),
    path('training/<str:username>/', TrainingView.as_view(), name="training"),
    path('attendance/<str:username>/', AttendanceList.as_view(), name="attendance-history")

]
