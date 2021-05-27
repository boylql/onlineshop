import uuid
import datetime

import jsonpickle
from django.db.models import F
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render

# Create your views here.
from cartapp.cartmanager import getCartManger
from goodsapp.models import Inventory
from orderapp.models import Order, OrderItem
from orderapp.ordermanager import getOrderManger
from userapp.models import Address
from utils.alipay import AliPay


def order_view(request):
    # 获取请求参数
    cartitems = request.GET.get('cartitems', '')
    orderid = request.GET.get('orderid', '')
    # 获取当前用户的登录信息
    user = request.session.get('user', '')
    # 判断用户是否登录
    if cartitems != '':
        if not user:
            return HttpResponseRedirect('/user/login/?redirct=order&cartitems=' + cartitems)
        return HttpResponseRedirect('/order/toOrder/?cartitems=' + cartitems)
    if orderid != '':
        return HttpResponseRedirect('/order/goOrder/?orderid=' + orderid)


def queryAll(request):
    # 获取cartmanager对象
    orderManager = getOrderManger(request)
    # 获取当前登录用户购物项表中的所有信息
    orderList = orderManager.queryAll()
    return render(request, 'orderview.html', {'orderList': orderList})


def toOrder(request):
    cartitems = request.GET.get('cartitems', '')
    # 将cartitems进行反序列化
    cartitemsList = jsonpickle.loads(cartitems)
    cartItemObjList = [getCartManger(request).get_cartitems(**eval(ci)) for ci in cartitemsList if ci]
    # 获取用户的默认收件地址
    user = jsonpickle.loads(request.session.get('user'))
    addr = user.address_set.get(isdefault=True)
    # 支付总金额
    totalPrice = 0
    for cio in cartItemObjList:
        totalPrice += cio.getTotalPrice()
    return render(request, 'order.html', {'cartitemsList': cartItemObjList, 'addr': addr, 'totalPrice': totalPrice})


def goOrder(request):
    # 获取cartmanager对象
    orderManager = getOrderManger(request)
    orderid = request.GET.get('orderid', '')
    orderItemList = orderManager.findById(orderid)
    user = jsonpickle.loads(request.session.get('user'))
    addr = user.address_set.get(isdefault=True)
    totalPrice = 0
    for oio in orderItemList:
        totalPrice += oio.getTotalPrice()
    return render(request, 'order.html',
                  {'cartitemsList': orderItemList, 'addr': addr, 'totalPrice': totalPrice, 'orderid': orderid})


# 创建alipay对象
alipayObj = AliPay(appid='2021000117642543', app_notify_url='http://127.0.0.1:8000/order/checkPay/',
                   app_private_key_path='orderapp/keys/my_private_key.txt',
                   alipay_public_key_path='orderapp/keys/alipay_public_key.txt',
                   return_url='http://127.0.0.1:8000/order/checkPay/', debug=True)


def toPay(request):
    # 接收请求参数
    aid = request.GET.get('address', '')
    aid = int(aid)
    orderid = orderid = request.GET.get('orderid', '')
    addrObj = Address.objects.get(id=aid)
    payway = request.GET.get('payway', '')
    cartitems = request.GET.get('cartitems', '')
    cartitemList = jsonpickle.loads(cartitems)
    # 添加order表的信息
    params = {
        'out_trade_num': uuid.uuid4().hex,
        'order_num': datetime.datetime.today().strftime('%Y%m%d%H%M%S'),
        'payway': payway,
        'address': addrObj,
        'user': jsonpickle.loads(request.session.get('user'))
    }
    # 获取支付总金额
    totalPrice = request.GET.get('totalPrice')
    if orderid == '':
        orderObj = Order.objects.create(**params)
        # 添加OrderTtem表的信息
        orderItemList = [OrderItem.objects.create(order=orderObj, **ci) for ci in cartitemList if ci]
        alipayParams = alipayObj.direct_pay(subject=u'爱婴客', out_trade_no=orderObj.out_trade_num, total_amount=totalPrice)
    else:
        Order.objects.filter(id=orderid).update(out_trade_num=params['out_trade_num'])
        alipayParams = alipayObj.direct_pay(subject=u'爱婴客', out_trade_no=params['out_trade_num'],total_amount=totalPrice)

    url = alipayObj.gateway + '?' + alipayParams
    return HttpResponseRedirect(url)


def checkPay(request):
    params = request.GET.dict()
    orderid = orderid = request.GET.get('orderid', '')
    # 获取签名
    sign = params.pop('sign')
    # 获取当前登录用户对象
    user = jsonpickle.loads(request.session.get('user'))
    # 判断是否支付成功
    if alipayObj.verify(params, sign):
        # 修改订单信息
        if orderid != '':
            trade_num = params.get('trade_no')
            Order.objects.filter(id=orderid).update(status=u'待发货', trade_no=trade_num)
        else:
            out_trade_no = params.get('out_trade_no')
            trade_num = params.get('trade_no')
            order = Order.objects.get(out_trade_num=out_trade_no)
            order.status = u'待发货'
            order.trade_no = trade_num
            order.save()
        # 修改库存信息
        orderItemList = order.orderitem_set.all()
        [Inventory.objects.filter(goods_id=oi.goodsid).update(count=F('count') - oi.count) for oi in orderItemList if
         oi]
        # 清空购物车
        [user.cartitem_set.filter(goodsid=oi.goodsid).delete() for oi in orderItemList if oi]
        return HttpResponseRedirect('/order/queryAll/')
    return HttpResponse('支付失败！')


def confirm(request):
    orderid = orderid = request.GET.get('orderid', '')
    Order.objects.filter(id=orderid).update(status = '已完成')
    return HttpResponseRedirect('/order/queryAll/')