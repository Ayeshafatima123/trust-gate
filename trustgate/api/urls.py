from django.urls import path
from . import views

urlpatterns = [
    path("captcha/new", views.new_captcha, name="api_captcha_new"),
    path("captcha/verify", views.verify_captcha, name="api_captcha_verify"),
]
from django.urls import path
from . import views

urlpatterns = [
    path("hello/", views.hello_api, name="hello_api"),
]
from django.urls import path
from . import views

urlpatterns = [
    path("", views.api_home, name="api_home"),  # default /api/ routepython manage.py makemigrations --empty billing

]
from django.urls import path
from django.views.generic import TemplateView
from .views import PingView, KeysView

urlpatterns = [
    path("", TemplateView.as_view(template_name="api/docs.html")),
    path("ping", PingView.as_view()),
    path("keys", KeysView.as_view()),

]
