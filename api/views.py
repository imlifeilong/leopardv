from django.http import HttpResponse
from django.contrib.auth.models import User

from rest_framework.views import APIView
from rest_framework.decorators import api_view
from rest_framework.response import Response

import requests
import os

from api.models import Node, Deploy, Project
from api.serializers import NodeSerializer, ProjectSerializer
from api.utils import get_valid_img, uri, scrapyd_obj


def verify(request):
    return HttpResponse(get_valid_img(request))


class NodeList(APIView):
    '''节点列表'''

    def get_status(self, pk):
        # 节点状态
        try:
            node = Node.objects.get(nid=pk)
            resp = requests.get(uri(node.ip, node.port), timeout=0.1)
        except:
            return 0

        return 1 if resp.ok else 0

    def get(self, request):
        # 节点列表
        nodes = Node.objects.all()
        for node in nodes:
            node.status = self.get_status(node.nid)

        serializer = NodeSerializer(nodes, many=True)

        return Response(serializer.data)

    def post(self, request):
        # 刷新节点状态
        result = {'status': 1, 'msg': None, 'data': None}
        data = []
        for nid in request.POST.getlist('nids[]'):
            data.append({'nid': nid, 'status': self.get_status(nid)})
        result['data'] = data

        return Response(result)


class NodeDetail(APIView):
    def get_single(self, nid):
        return Node.objects.get(nid=nid)

    def get(self, request):
        nid = request.GET.get('nid')
        node = self.get_single(nid)
        serializer = NodeSerializer(node)
        return Response(serializer.data)


class ProjectList(APIView):
    def get_single(self, nid):
        return Node.objects.get(nid=nid)

    def get(self, request):
        username = request.session['username']
        nid = request.GET.get('nid')
        node = self.get_single(nid)
        projects = Project.objects.filter(user=User.objects.get(username=username), address=node.ip)
        serializer = ProjectSerializer(projects, many=True)

        return Response(serializer.data)

    def post(self, request):
        Project.objects.get(pk=request.POST.get('id')).delete()
        return Response()


def project_upload(request):
    if request.method == 'POST':
        file = request.FILES.get('project')
        description = request.POST.get('description')
        address = request.POST.get('address')

        user = User.objects.get(username=request.session['username'])
        name = file.name.replace('.zip', '') if file else ''
        # 已经上传过，删除，重传
        deploy = Project.objects.filter(name=name, address=address, user=user)
        if deploy:
            tmp = deploy[0]
            if os.path.exists(tmp.file.path):
                os.remove(tmp.file.path)
            tmp.delete()
    return HttpResponse()
