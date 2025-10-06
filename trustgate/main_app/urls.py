from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("signup/", views.signup, name="signup"),
    path("prd/", views.prd, name="prd"),
    path("upgrade/", views.upgrade, name="upgrade"),
    path("billing/complete/", views.billing_complete, name="billing_complete"),
]
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),  # Home page
]

from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
]
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
]
from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
]
from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
]
from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("success/", views.success_page, name="success"),
]
from django.urls import path
from . import views

urlpatterns = [
    path("success/", views.success_page, name="success"),
]
