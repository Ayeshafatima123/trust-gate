"""
URL configuration for trustgate project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    # Admin panel
    path('admin/', admin.site.urls),

    # Django-simple-captcha images/audio
    path('captcha/', include('captcha.urls')),

    # Apna captcha_app routes
    path('', include('captcha_app.urls')),

    

    # Billing routes
    path('billing/', include('billing.urls')),

    # API routes (agar use ho rahe hain)
    path('api/', include('api.urls')),

]


from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("captcha_app.urls")),   # 👈 root path yahan add karo
    path("accounts/", include("accounts.urls")),
    path("billing/", include("billing.urls")),
    path("api/", include("api.urls")),
]
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("main_app.urls")),       # 👈 ab empty path home se map ho jayega
    path("captcha/", include("captcha_app.urls")),
    path("accounts/", include("accounts.urls")),
    path("billing/", include("billing.urls")),
    path("api/", include("api.urls")),
]
from django.contrib import admin
from django.urls import path, include
from captcha_app import views as captcha_views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", captcha_views.home, name="home"),  # home page

    # Captcha app (only once with namespace)
    path("captcha/", include(("captcha_app.urls", "captcha_app"), namespace="captcha_app")),

    # Accounts app (only once with namespace)


    # API
    path("api/", include("api.urls")),

    # Billing
    path("billing/", include(("billing.urls", "billing"), namespace="billing")),

    path("captcha/", include("captcha.urls")),  # ✅ important
    
  
    path("accounts/", include(("accounts.urls", "accounts"), namespace="accounts")),
    
    path("auth/", include(("django.contrib.auth.urls", "auth"), namespace="auth")),   # ✅ different

]








