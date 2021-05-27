# coding=utf-8

from collections import OrderedDict

from orderapp.models import Order
from django.db.models import F
import jsonpickle


class OrderManager(object):

    def queryAll(self, *args, **kwargs):
        ''':return CartItem  多个购物项'''
        pass


# 用户已登录
class DBOrderManger(OrderManager):
    def __init__(self, user):
        self.user = user

    def queryAll(self, *args, **kwargs):

        return self.user.order_set.order_by('id').filter().all()

    def findById(self, id):
        return self.user.order_set.get(id=id).getOrderItem()

import jsonpickle


# 工厂方法
# 根据当前用户是否登录返回相应的CartManger对象
def getOrderManger(request):
    if request.session.get('user'):
        # 当前用户已登录
        return DBOrderManger(jsonpickle.loads(request.session.get('user')))
