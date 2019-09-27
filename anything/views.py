from django.shortcuts import render, redirect
from django.contrib import auth

from rest_framework.decorators import api_view
from rest_framework.response import Response


def index(request):
    return render(request, 'index.html')


def node(request):
    return render(request, 'node.html')


def node_detail(request, nid):
    return render(request, 'node_detail.html', {'nid': nid})


@api_view(['GET', 'POST'])
def login(request):
    result = {'status': 1, 'msg': None, 'data': None}

    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        checkcode = request.POST['checkcode'].upper()

        if checkcode and checkcode == request.session['checkcode']:
            user = auth.authenticate(username=username, password=password)

            if user:
                auth.login(request, user)
                request.session['username'] = username
                result['data'] = '/'

            else:
                result['status'], result['msg'] = 0, '用户名或密码错误！'
        else:
            result['status'], result['msg'] = 0, '验证码错误！'

        return Response(result)

    return render(request, 'login.html')


def logout(request):
    auth.logout(request)
    return redirect('/login/')
