from django.urls import path
from .views import LoginView, AddUserView, CaptureView, AllUserListView, UserListView, logout, UploadImageView

app_name = 'accounts'
urlpatterns = [
    path('login/', LoginView.as_view(), name='login'),
    path('create/', AddUserView.as_view(), name='create'),
    path('lists/', AllUserListView.as_view(), name='list'),
    path('profile/<int:pk>/', UserListView.as_view(), name="profile"),
    path('capture/<str:username>/', CaptureView.as_view(), name="capture"),
    path('logout/', logout, name='logout'),
    path('<int:pk>/upload/', UploadImageView.as_view(), name='dataset')
]

# (?P<user_name>\w+)