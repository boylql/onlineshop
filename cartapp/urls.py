from django.urls import path

from cartapp import views

urlpatterns = [
    path('', views.CartView.as_view()),
    path('queryAll/', views.queryAll),

]