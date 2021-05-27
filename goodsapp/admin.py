from django.contrib import admin
from goodsapp import models

# Register your models here.
class CategoryAdmin(admin.ModelAdmin):
    # 添加显示的字段名
    list_display = ['id','cname']
    # 设置可编辑字段
    list_editable = ['cname']

class GoodsAdmin(admin.ModelAdmin):
    # 添加显示的字段名
    list_display = ['id','oldprice','price']
    # 设置可编辑字段
    list_editable = ['price']

class InventoryAdmin(admin.ModelAdmin):
    # 添加显示的字段名
    list_display = ['id','count']
    # 设置可编辑字段
    list_editable = ['count']
admin.site.register(models.Goods,GoodsAdmin)
admin.site.register(models.Category,CategoryAdmin)
admin.site.register(models.Inventory,InventoryAdmin)
