"""ayk_netmall URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
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

from django.urls import path, re_path

from goodsapp import views

urlpatterns = [
    path('', views.IndexView.as_view()),
    path('discount/', views.DiscountView.as_view()),
    re_path('discount/page/(?P<num>\d+)$', views.DiscountView.as_view()),
    re_path('category/(?P<cid>\d+)$', views.IndexView.as_view()),
    re_path('category/(?P<cid>\d+)/page/(?P<num>\d+)$', views.IndexView.as_view()),
    re_path('goodsdetails/(\d+)$', views.DetailView.as_view()),
    path('IntelligentRecommendation/',views.IntelligentRecommendation.as_view())
]
