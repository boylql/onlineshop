import math

from django.db import models

# Create your models here.
from goodsapp.models import Goods
from userapp.models import Address, UserInfo


class Order(models.Model):
    out_trade_num = models.UUIDField()
    order_num = models.CharField(max_length=50)
    trade_no = models.CharField(max_length=120,default='')
    status = models.CharField(max_length=20,default=u'待支付')
    payway = models.CharField(max_length=20,default='alipapa')
    address = models.ForeignKey(Address,on_delete=models.DO_NOTHING)
    user = models.ForeignKey(UserInfo,on_delete=models.DO_NOTHING)

    def getOrderItem(self):
        return OrderItem.objects.filter(order=self.id)

    def getAddress(self):
        return Address.objects.get(id=self.address)

class OrderItem(models.Model):
    goodsid = models.PositiveIntegerField()
    count = models.PositiveIntegerField()
    order = models.ForeignKey(Order,on_delete=models.DO_NOTHING)

    def getGoods(self):
        return Goods.objects.get(id=self.goodsid)

    def getTotalPrice(self):
        if self.getGoods().price:
            return (int(self.count) * self.getGoods().price)
        else:
            return (int(self.count) * self.getGoods().oldprice)
