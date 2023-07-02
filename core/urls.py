from django.urls import path
from .views import RegisterAPIView
from .views import LoginAPIView, UserAPIView

urlpatterns = [
    path('register', RegisterAPIView.as_view()),
    path('login', LoginAPIView.as_view()),
    path('user', UserAPIView.as_view()),
]
