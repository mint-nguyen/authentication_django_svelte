from django.urls import path
from .views import RegisterAPIView, RefreshAPIView
from .views import LoginAPIView, UserAPIView, LogoutAPIView

urlpatterns = [
    path('register', RegisterAPIView.as_view()),
    path('login', LoginAPIView.as_view()),
    path('user', UserAPIView.as_view()),
    path('refresh', RefreshAPIView.as_view()),
    path('logout', LogoutAPIView.as_view()),
]
