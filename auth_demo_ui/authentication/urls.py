from django.urls import path
from . import views

urlpatterns = [
    path('', views.test, name='root'),
    path('authenticate/', views.authenticate, name='authenticate'),
    path('request/otp/<int:pcn>', views.requestOTP, name='request_otp')
]