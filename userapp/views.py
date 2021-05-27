import os

from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from django.shortcuts import render

# Create your views here.
from django.views import View
from lxml.html.builder import IMG

from ayk_netmall import settings
from cartapp.cartmanager import SessionCartManager
from userapp.models import UserInfo, Area, Address, profile
import jsonpickle


class RegisterView(View):
    def get(self, request):
        return render(request, 'register.html')

    def post(self, request):
        account = request.POST.get('account');
        pwd = request.POST.get('password');
        # 数据库中查询当前的用户是否存在
        userList = UserInfo.objects.filter(uname=account)
        if userList:
            return HttpResponseRedirect('/user/register/')
        else:
            # 将用户名和密码插入到数据库
            user = UserInfo.objects.create(uname=account, pwd=pwd)
            # 给用户设置默认的头像和个性签名
            profile.objects.create(pprofile='这人很懒，什么都没有写', purl='/static/tx.png', userinfo=user)
        # 判断注册成功与否
        if user:
            # 将当前注册用户对象保存到session
            request.session['user'] = jsonpickle.dumps(user)
            return HttpResponseRedirect('/user/center/')
        return HttpResponseRedirect('/user/register/')


class CenterView(View):
    def get(self, request):
        user = jsonpickle.loads(request.session.get('user'))
        profile = user.profile_set.all()
        if profile:
            return render(request, 'center.html', {'profile': profile[0], 'user': user})
        else:
            return render(request, 'center.html', {'profile': '', 'user': user})


class LoginView(View):
    def get(self, request):
        return render(request, 'login.html',
                      {'redirct': request.GET.get('redirct', ''), 'cartitems': request.GET.get('cartitems', '')})

    def post(self, request):
        # 获取请求参数
        uname = request.POST.get('account', '')
        pwd = request.POST.get('password', '')
        redirect = request.POST.get('redirect', '')
        # 数据库中查询当前的用户是否存在
        userList = UserInfo.objects.filter(uname=uname, pwd=pwd)
        # 判断是否登录成功
        if userList:
            # 将用户信息存入session中
            print('登录成功')
            request.session['user'] = jsonpickle.dumps(userList[0])
            SessionCartManager(request.session).migrateSession2DB()
            if redirect == 'cart':
                return HttpResponseRedirect('/cart/queryAll/')
            elif redirect == 'order':
                # 将session中的购物项转移到数据库中
                return HttpResponseRedirect('/order/toOrder/?cartitems=' + request.POST.get('cartitems', ''))
            return HttpResponseRedirect('/user/center/')
        return HttpResponseRedirect('/user/login/')


from utils.code import *


class LoadCodeView(View):
    def get(self, request):
        # 调用工具包下的函数生成验证码
        img, txt = gene_code()
        # 将txt保存到session
        request.session['sessionCode'] = txt
        # 响应页面
        return HttpResponse(img, content_type='image/png')


class CheckCodeView(View):
    def get(self, request):
        # 获取请求参数
        code = request.GET.get('code', '')
        # 获取系统生成的验证码
        sessioncode = request.session.get('sessionCode')
        flag = code == sessioncode
        return JsonResponse({'flag': flag})


class CheckPwdView(View):
    def get(self, request):
        # 获取请求参数
        pwd = request.GET.get('pwd', '')
        # 获取系统生成的验证码
        user = jsonpickle.loads(request.session.get('user'))
        flag = pwd == user.pwd
        return JsonResponse({'flag': flag})


class Logout(View):
    def get(self, request):
        # 清空session对象中的所有数据
        request.session.clear()
        return JsonResponse({'flag': True})


class AddressView(View):
    def get(self, request):
        # 获取当前登录用户对象
        user = jsonpickle.loads(request.session.get('user'))
        addrList = user.address_set.all()
        profile = user.profile_set.all()
        if profile:
            return render(request, 'adress.html', {'profile': profile[0], 'addrList': addrList})
        else:
            return render(request, 'adress.html', {'profile': '', 'addrList': addrList})

    def post(self, request):
        params = request.POST.dict()
        params.pop('csrfmiddlewaretoken')
        # 获取当前登录用户对象
        user = jsonpickle.loads(request.session.get('user'))
        flag = request.POST.get('flag','')
        addrid = request.POST.get('addrid','')
        if flag == 'delete':
            user.address_set.filter(id=addrid).update(isdelete = True)
        elif flag == 'default':
            user.address_set.all().update(isdefault = False)
            user.address_set.filter(id=addrid).update(isdefault = True)
        else:
            Address.objects.create(userinfo=user,
                               isdefault=(lambda count: True if count == 0 else False)(user.address_set.count()),isdelete = False,
                               **params)
        return HttpResponseRedirect('/user/address/')


from django.core.serializers import serialize


def loadAddr(request):
    # 获取请求参数
    pid = request.GET.get('pid', -1)
    pid = int(pid)
    # 根据父id查询区划信息
    areaList = Area.objects.filter(parentid=pid)
    # 序列化areaList
    jareaList = serialize('json', areaList)
    return JsonResponse({'jareaList': jareaList})


class UpdateView(View):
    def get(self, request):
        # 获取当前登录用户对象
        user = jsonpickle.loads(request.session.get('user'))
        profile = user.profile_set.all()
        if profile:
            return render(request, 'update.html', {'profile': profile[0], 'user': user})
        else:
            return render(request, 'update.html', {'profile': '', 'user': user})

    def post(self, request):
        #获取当前的登录对象
        user = jsonpickle.loads(request.session.get('user'))
        #获取请求数据
        params = request.POST.dict()
        params.pop('csrfmiddlewaretoken')
        # 获取文件
        img = request.FILES.get('purl')
        #判断是否有传递图片文件
        if img:
            # 创建一个文件
            save_path = '%s/face/%s' % (settings.MEDIA_ROOT, img.name)
            with open(save_path, 'wb') as f:
                # 获取上传文件的内容并写到创建的文件中
                for content in img.chunks():
                    f.write(content)
            if profile.objects.filter(userinfo=user):
                profile.objects.filter(userinfo=user).update(purl='/media/face/%s' % img.name)
            else:
                profile.objects.create(purl='/media/face/%s' % img.name, userinfo=user)
        if params['pprofile']:
            if profile.objects.filter(userinfo=user):
                profile.objects.filter(userinfo=user).update(pprofile=params['pprofile'])
            else:
                profile.objects.create(pprofile=params['pprofile'], userinfo=user)
        if params['pwd_now']:
            UserInfo.objects.filter(uname=user.uname).update(pwd=params['pwd_now'])
        return HttpResponseRedirect('/user/center/')
