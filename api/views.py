from django.http import HttpResponse
from django.contrib.auth.models import User

from rest_framework.views import APIView
from rest_framework.decorators import api_view
from rest_framework.response import Response

import requests
import os
import zipfile

from api.models import Node, Deploy, Project
from api.serializers import NodeSerializer, ProjectSerializer
from api.utils import get_valid_img, uri, scrapyd_obj, delete_file, modify_file


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
        projects = Project.objects.filter(user=User.objects.get(username=username), node=node)
        serializer = ProjectSerializer(projects, many=True)

        return Response(serializer.data)

    def post(self, request):
        result = {'status': 1, 'msg': None, 'data': None}
        # 删除部署记录
        project = Project.objects.get(pk=request.POST.get('id'))
        node = Node.objects.get(nid=request.POST.get('nid'))
        scrapyd = scrapyd_obj(uri(node.ip, node.port))
        if scrapyd:
            # 删除部署的工程
            scrapyd.delete_project(project.name)
        # 删除文件
        delete_file(project.file.path)
        # 删除记录
        project.delete()
        result['msg'] = '工程 %s 已经删除！' % project.name
        return Response(result)


class JobList(APIView):
    # 作业

    # def get_jobs(self):
    def get(self, request):
        per = 10
        result = {'status': 1, 'msg': None, 'data': None}
        # 当前用户所有spider
        user = User.objects.get(username=request.session['username'])
        spiders_list = []
        projects_list = []
        nodes_cache = {}
        for project in user.project_set.all():

            projects_list.append({'ip': project.node.ip, 'project': project.name})
            if project.node.ip in nodes_cache:
                scrapyd = nodes_cache[project.node.ip]
            else:
                scrapyd = scrapyd_obj(uri(project.node.ip, project.node.port))
                nodes_cache[project.node.ip] = scrapyd

            if scrapyd:
                spiders = scrapyd.list_spiders(project.name)
                spiders_tmp_list = [{'node': project.node.nid.__str__(), 'project': project.name, 'spider': spider}
                                    for spider in spiders]
                spiders_list.extend(spiders_tmp_list)
        result['data'] = {}
        result['data']['spiders'] = spiders_list
        result['data']['projects'] = projects_list
        return Response(result)


@api_view(['GET', 'POST'])
def project_upload(request):
    # 工程部署
    result = {'status': 1, 'msg': None, 'data': None}
    try:
        if request.method == 'POST':
            file = request.FILES.get('project')
            # 判断是否上传文件
            if not file:
                result['status'], result['msg'] = 0, '请选择上传工程文件'
                return Response(result)
            description = request.POST.get('description')
            node = Node.objects.get(nid=request.POST.get('nid'))
            user = User.objects.get(username=request.session['username'])

            name = file.name.replace('.zip', '') if file else ''

            # 已经上传过，删除记录和文件，重传
            deploy = Project.objects.filter(name=name, node=node, user=user)

            if deploy:
                tmp = deploy[0]
                if os.path.exists(tmp.file.path):
                    os.remove(tmp.file.path)
                tmp.delete()

            new_obj = Project.objects.create(name=name, file=file, node=node, user=user, description=description)
            # 解压文件
            f = zipfile.ZipFile(new_obj.file.path)
            filepath = os.path.split(new_obj.file.path)[0]
            f.extractall(path=filepath)
            f.close()

            # 修改配置文件
            url = 'http://%s:%s/' % (node.ip, node.port)
            config_file = os.path.join(filepath, name + os.sep + 'scrapy.cfg')
            modify_file(config_file, 'url = %s' % url)

            # 部署文件
            scrapyd = scrapyd_obj(url)
            if scrapyd:
                # 删除原来版本
                versions = scrapyd.list_versions(name)
                for v in versions:
                    scrapyd.delete_version(name, v)

                cur_dir = os.getcwd()
                # 重新部署
                os.chdir(os.path.join(filepath, name))

                with os.popen('scrapyd-deploy') as cmd:
                    print(cmd.read())

                os.chdir(cur_dir)

        result['msg'] = '%s 工程部署成功！' % name
    except Exception as e:
        result['msg'] = str(e)
    return Response(result)
