from django.urls import path

from orderapp import views

urlpatterns = [
    path('', views.order_view),
    path('queryAll/', views.queryAll),
    path('toOrder/', views.toOrder),
    path('goOrder/', views.goOrder),
    path('toPay/', views.toPay),
    path('checkPay/', views.checkPay),
    path('confirm/', views.confirm)

]
