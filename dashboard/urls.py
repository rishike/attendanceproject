from django.urls import path
from .views import DashboardView, MarkAttendanceView, TrainingView

app_name = 'dashboard'

urlpatterns = [
    path('dashboard/', DashboardView.as_view(), name='home'),
    path('markattendance/', MarkAttendanceView.as_view(), name='mark-attendance'),
    path('training/<str:username>/', TrainingView.as_view(), name="training")

]
