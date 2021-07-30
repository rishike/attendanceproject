from django.urls import path
from .views import DashboardView, MarkAttendanceView

urlpatterns = [
    path('dashboard/', DashboardView.as_view(), name='dashboard'),
    path('markattendance/', MarkAttendanceView.as_view(), name='mark-attendance'),
]
