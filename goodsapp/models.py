from django.db import models
import collections

# Create your models here.
class Category(models.Model):
    cname = models.CharField(max_length=10)

    def __str__(self):
        return '<Category:%s>'%self.cname

class Goods(models.Model):
    gname = models.CharField(max_length=100,unique=True)
    oldprice = models.DecimalField(max_digits=5,decimal_places=2,null=True)
    price = models.DecimalField(max_digits=5,decimal_places=2)
    gurl = models.CharField(max_length=255)
    gdurl = models.CharField(max_length=255)
    goodsdetails = models.TextField(null=True)
    category = models.ForeignKey(Category,on_delete=models.DO_NOTHING)

    def __str__(self):
        return '<Goods:%s>'%self.gname

    def getInventory(self):
        return Inventory.objects.get(goods=self.id)

class Inventory(models.Model):
    count = models.PositiveIntegerField(default=100)
    goods = models.ForeignKey(Goods,on_delete=models.DO_NOTHING)