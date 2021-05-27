import math

from django.db import models

# Create your models here.
from goodsapp.models import Goods
from userapp.models import UserInfo


class CartItem(models.Model):
    goodsid = models.PositiveIntegerField()
    count = models.PositiveIntegerField()
    isdelete = models.BooleanField(default=False)
    user = models.ForeignKey(UserInfo,on_delete=models.DO_NOTHING)
    def getGoods(self):
        return Goods.objects.get(id=self.goodsid)

    def getTotalPrice(self):
        if self.getGoods().price:
            return (int(self.count) * self.getGoods().price)
        else:
            return (int(self.count) * self.getGoods().oldprice)