# accounts/urls.py
from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = "accounts"

urlpatterns = [
    path("signup/", views.signup_view, name="signup"),  # custom signup
    path("login/", auth_views.LoginView.as_view(template_name="accounts/login.html"), name="login"),  # built-in login
    path("logout/", auth_views.LogoutView.as_view(next_page="home"), name="logout"),  # logout redirect to home

]
# accounts/urls.py
from django.urls import path
from . import views

app_name = "accounts"

urlpatterns = [
    path("", views.account_dashboard, name="dashboard"),  # 👈 accounts/ par dashboard milega
    path("signup/", views.signup_view, name="signup"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("withdraw/", views.withdraw, name="withdraw"),  # 👈 yeh add karo
    path("wallet/", views.my_wallet, name="my_wallet"),

]
