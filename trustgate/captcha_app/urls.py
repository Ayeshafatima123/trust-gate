from django.urls import path
from . import views

app_name = "captcha_app"  # ✅ namespace optional, recommended

urlpatterns = [
    path('', views.home, name='home'),                     # home page
    path('captcha-test/', views.captcha_view, name='captcha_page'),  # captcha test
    path('success/', views.success_view, name='success'),  # success page
]


from django.urls import path
from . import views

app_name = "captcha_app"   # 👈 namespace yahan define karna zaroori hai

urlpatterns = [
    path("", views.captcha_view, name="captcha_page"),   # 👈 empty ra
    path("success/", views.success_view, name="success"),

]
# captcha_app/urls.py
from django.urls import path
from . import views

app_name = "captcha_app"  # yeh zaroori hai agar aap namespaced url use karte ho

urlpatterns = [
    path("test/", views.captcha_view, name="captcha_page"),
    path("success/", views.success_view, name="success"),
     path("solve/<int:task_id>/", views.solve_captcha, name="solve_captcha"),
]


from django.urls import path
from . import views

urlpatterns = [
    path("captcha/page/", views.captcha_view, name="captcha_page"),  # ✅ correct
    path("captcha/success/", views.success_view, name="success"),
    path("captcha/solve/<int:task_id>/", views.solve_captcha, name="solve_captcha"),

]
from django.urls import path
from . import views

app_name = "captcha_app"

urlpatterns = [
    path("", views.home, name="home"),
    path("solve/<int:task_id>/", views.solve_captcha, name="solve_captcha")
]

from django.urls import path
from . import views

app_name = "captcha_app"   # namespace define karna zaruri hai

urlpatterns = [
    path("", views.home, name="home"),
    path("captcha-test/", views.captcha_view, name="captcha_page"),
    path("success/", views.success_view, name="success"),
    path("withdraw/", views.withdraw_view, name="withdraw"),
    path("solve/<int:captcha_id>/", views.solve_captcha, name="solve_captcha"),

]


