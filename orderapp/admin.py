from django.contrib import admin
from orderapp import models
# Register your models here.
class OrderAdmin(admin.ModelAdmin):
    # 添加显示的字段名
    list_display = ['id','status']
    # 设置可编辑字段
    list_editable = ['status']
    # # 添加检索项:同时按照下面的条件进行检索
    # search_fields = ['title', 'content', 'desc', 'click_num', 'love_num', 'user']
    # # 直接可以在页面上编辑
    # list_editable = ['title', 'click_num', 'love_num']
    # # 过滤器
    # list_filter = ['date', 'user', 'click_num']

admin.site.register(models.Order,OrderAdmin)
