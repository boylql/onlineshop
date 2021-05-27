from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render

# Create your views here.
from django.views import View

from cartapp.cartmanager import *


class CartView(View):
    def post(self,request):
        #这句话的设置是为了保证数据能够实时保存到session中
        request.session.modified = True
        #获取用户当前操作类型变量值
        flag = request.POST.get('flag','')
        #判断用户当前操作类型
        if flag == 'add':
            # 获取cartmanager对象
            cartManager = getCartManger(request)
            #加入购物车操作
            cartManager.add(**request.POST.dict())
        elif flag == 'plus':
            # 获取cartmanager对象
            cartManager = getCartManger(request)
            #增加商品数量
            cartManager.update(step=1,**request.POST.dict())
        elif flag == 'minus':
            # 获取cartmanager对象
            cartManager = getCartManger(request)
            #减少商品数量
            cartManager.update(step=-1,**request.POST.dict())
        elif flag == 'delete':
            # 获取cartmanager对象
            cartManager = getCartManger(request)
            # 删除商品
            cartManager.delete(**request.POST.dict())
        return HttpResponseRedirect('/cart/queryAll/')


def queryAll(request):
    # 获取cartmanager对象
    cartManager = getCartManger(request)
    #获取当前登录用户购物项表中的所有信息
    cartItemList = cartManager.queryAll()
    return render(request,'cart.html',{'cartItemList':cartItemList})