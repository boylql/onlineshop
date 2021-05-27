import math
from pprint import pprint

import jsonpickle
from django.db.models import Q
from django.shortcuts import render
from django.views import View
# Create your views here.
from goodsapp.models import Category, Goods
from django.core.paginator import Paginator

from orderapp.models import Order, OrderItem
from userapp.models import UserInfo
import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import pairwise_distances


class IndexView(View):
    def get(self, request, cid=1, num=1):
        recommend(request)
        # # 获取请求参数
        gname = request.GET.get('find', '')
        print(gname)
        cid = int(cid)
        num = int(num)
        # 查询所有类别信息
        categoryList = Category.objects.all()
        # 查询当前类别下的所有商品信息
        # goodsList = Goods.objects.filter(category_id=cid).order_by('id')
        goodsList = Goods.objects.filter(Q(category_id=cid) & Q(gname__icontains=gname)).order_by('id')
        if gname!='':
            goodsList = Goods.objects.filter(gname__icontains=gname).order_by('id')
        # 创建分页器对象
        paginator_obj = Paginator(goodsList, 8)
        # 获取某一页的数据对象
        page_obj = paginator_obj.page(num)
        # 获取每一页显示的页码范围
        begin = num - int(math.ceil(10.0 / 2))
        if begin < 1:
            begin = 1
        end = begin + 9
        if end > paginator_obj.num_pages:
            end = paginator_obj.num_pages
        if end < 10:
            begin = 1
        else:
            begin = end - 9
        page_list = range(begin, end + 1)
        return render(request, 'index.html',
                      {'categoryList': categoryList, 'cid': cid, 'goodsList': page_obj, 'page_list': page_list,
                       'num': num})

def recommend_view(func):
    def _wrapper(detailView, request, goodsid, *args, **kwargs):
        # 从cookie中获取用户访问的所在商品id
        c_goodsid = request.COOKIES.get('rem', '')
        # 存放用户访问商品的goodsid列表
        # ['1','2','3'] = '1 2 3'
        goodsIdList = [gid for gid in c_goodsid.split() if gid.strip()]
        # 最终推荐的商品列表
        goodsObjList = [Goods.objects.get(id=vgoodsid) for vgoodsid in goodsIdList if
                        Goods.objects.get(id=vgoodsid).category_id == Goods.objects.get(
                            id=goodsid).category_id and vgoodsid != goodsid][:4]
        # 调用相应修饰的函数
        response = func(detailView, request, goodsid, goodsObjList, *args, **kwargs)
        # 判断用户访问商品是否存在goodsIdList中
        if goodsid in goodsIdList:
            goodsIdList.remove(goodsid)
            goodsIdList.insert(0, goodsid)
        else:
            goodsIdList.insert(0, goodsid)
        # 将用户访问的商品id存放至cookie
        response.set_cookie('rem', ' '.join(goodsIdList), max_age=3 * 24 * 60 * 60)
        return response

    return _wrapper


class DetailView(View):
    @recommend_view
    def get(self, request, goodsid, recommend_list=[]):
        goodsid = int(goodsid)
        # 根据商品id查询商品详情
        goods = Goods.objects.get(id=goodsid)
        return render(request, 'detail.html', {'goods': goods, 'recommend_list': recommend_list})


class DiscountView(View):
    def get(self, request, cid=1, num=1):
        cid = int(cid)
        num = int(num)
        categoryList = Category.objects.all()
        goodsList =Goods.objects.exclude(price__isnull=True).order_by('id')
        print(goodsList)
        # 创建分页器对象
        paginator_obj = Paginator(goodsList, 8)
        # 获取某一页的数据对象
        page_obj = paginator_obj.page(num)
        # 获取每一页显示的页码范围
        begin = num - int(math.ceil(10.0 / 2))
        if begin < 1:
            begin = 1
        end = begin + 9
        if end > paginator_obj.num_pages:
            end = paginator_obj.num_pages
        if end < 10:
            begin = 1
        else:
            begin = end - 9
        page_list = range(begin, end + 1)
        return render(request, 'discount.html',
                      {'categoryList': categoryList, 'goodsList': page_obj, 'page_list': page_list,
                       'num': num})


def recommend(request):
    user1 = jsonpickle.loads(request.session.get('user'))
    users = []
    for user in UserInfo.objects.filter().order_by('id').all():
        users.append(user.id)
    print(users)
    items = []
    for item in Goods.objects.filter().order_by('id').all():
        items.append(item.id)
    print(items)
    datasets = []
    for user in users:
        nums = [0 for i in range(len(items))]
        orders = Order.objects.order_by('id').filter(user_id=user).all()
        for order in orders:
            orderitems = OrderItem.objects.order_by('id').filter(order_id=order.id).all()
            print(orderitems)
            for orderitem in orderitems:
                j = items.index(orderitem.goodsid)
                nums[j] = 1
        datasets.append(nums)
    print(datasets)
    #计算所有数据两两的杰卡德相似系数
    df = pd.DataFrame(datasets,columns=items,index=users)
    pprint(df)
    #计算用户间的相似度
    user_similar = 1 - pairwise_distances(df.values,metric="jaccard")
    user_similar = pd.DataFrame(user_similar,columns=users,index=users)
    print("用户之间的相似度:")
    print(user_similar)
    topN_users = {}
    #遍历每一行数据
    for i in user_similar.index:
        #取出每一列数据，并删除自身，然后排序数据
        _df = user_similar.loc[i].drop([i])
        _df_sorted = _df.sort_values(ascending=False)
        top2 = list(_df_sorted.index[:2])
        topN_users[i] = top2
    print("Top2相似用户:")
    pprint(topN_users)
    #构建推荐结果
    rs_results = {}
    for user,sim_users in topN_users.items():
        #存储推荐结果
        rs_result = set()
        for sim_user in sim_users:
            #构建初始的推荐结果
            rs_result = rs_result.union(set(df.loc[sim_user].replace(0,np.nan).dropna().index))
        #过滤掉已经购买过的物品
        rs_result -= set(df.loc[user].replace(0,np.nan).dropna().index)
        rs_results[user] = rs_result
    print("最终的推荐结果")
    pprint(rs_results)
    print(type(rs_results[1]))
    return None

#协同过滤智能推荐
class IntelligentRecommendation(View):
    def get(self,request):
        user1 = jsonpickle.loads(request.session.get('user'))
        users = []
        for user in UserInfo.objects.filter().order_by('id').all():
            users.append(user.id)
        items = []
        for item in Goods.objects.filter().order_by('id').all():
            items.append(item.id)
        datasets = []
        #将每个用户的购买记录存入矩阵中
        for user in users:
            nums = [0 for i in range(len(items))]
            orders = Order.objects.order_by('id').filter(user_id=user).all()
            for order in orders:
                orderitems = OrderItem.objects.order_by('id').filter(order_id=order.id).all()
                for orderitem in orderitems:
                    j = items.index(orderitem.goodsid)
                    nums[j] = 1
            datasets.append(nums)
        #计算所有数据两两的杰卡德相似系数
        df = pd.DataFrame(datasets,columns=items,index=users)
        pprint(df)
        #计算用户间的相似度
        user_similar = 1 - pairwise_distances(df.values,metric="jaccard")
        user_similar = pd.DataFrame(user_similar,columns=users,index=users)
        topN_users = {}
        #遍历每一行数据
        for i in user_similar.index:
            #取出每一列数据，并删除自身，然后排序数据
            _df = user_similar.loc[i].drop([i])
            _df_sorted = _df.sort_values(ascending=False)
            top2 = list(_df_sorted.index[:2])
            topN_users[i] = top2
        #构建推荐结果
        rs_results = {}
        for user,sim_users in topN_users.items():
            #存储推荐结果
            rs_result = set()
            for sim_user in sim_users:
                #构建初始的推荐结果
                rs_result = rs_result.union(set(df.loc[sim_user].replace(0,np.nan).dropna().index))
            #过滤掉已经购买过的物品
            rs_result -= set(df.loc[user].replace(0,np.nan).dropna().index)
            rs_results[user] = rs_result
        goodsList = []
        goods = []
        for i in rs_results[user1.id]:
            goodsList.append(Goods.objects.get(id=i))
        for i in range(len(goodsList)-1):
            goods.append(goodsList[i])
        goods1 = goodsList[len(goodsList)-1]
        return render(request, 'recommend.html', {'goodsList': goodsList})