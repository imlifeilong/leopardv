from django.http import HttpResponse
from django.conf import settings
from django.contrib.auth.models import User

from rest_framework.views import APIView
from rest_framework.decorators import api_view
from rest_framework.response import Response

import requests
import os
import zipfile

from api.models import Node, Project, Job
from api.serializers import NodeSerializer, ProjectSerializer
from api.utils import get_valid_img, uri, scrapyd_obj, delete_file, modify_file, get_pages


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
        condition = {}
        condition['user'] = User.objects.get(username=request.session['username'])
        nid = request.GET.get('nid')
        if not nid.startswith('999'):
            condition['node'] = self.get_single(nid)

        projects = Project.objects.filter(**condition)
        serializer = ProjectSerializer(projects, many=True)

        return Response(serializer.data)

    def post(self, request):
        result = {'status': 1, 'msg': None, 'data': None}
        # 删除部署记录
        project = Project.objects.get(pk=request.POST.get('id'))
        node = Node.objects.get(nid=request.POST.get('nid'))
        scrapyd = scrapyd_obj(uri(node.ip, node.port))
        if scrapyd:
            if project.name in scrapyd.list_projects():
                # 删除部署的工程
                scrapyd.delete_project(project.name)

        if project.file:
            # 删除文件
            delete_file(project.file.path)
        else:
            delete_file(settings.MEDIA_ROOT + '/deploy/%s.zip' % project.name)

        # 删除记录
        project.delete()

        result['msg'] = '工程 %s 已经删除！' % project.name
        return Response(result)


class JobList(APIView):
    # 作业
    def get(self, request):
        per = 10
        result = {'status': 1, 'msg': None, 'data': None}
        page = int(request.GET.get('page', 1))
        # 当前用户所有spider
        user = User.objects.get(username=request.session['username'])
        spiders_list = []
        projects_list = []
        nodes_cache = {}
        for job in Job.objects.filter(user=user):

            if job.node in nodes_cache:
                node = nodes_cache[job.node]
            else:
                node = Node.objects.get(pk=job.node)
            nodes_cache[job.node] = node
            if job.status == 1:
                spiders_list.append({'node': job.node, 'project': job.project, 'spider': job.name, 'ip': node.ip})

            project_dict = {'ip': node.ip, 'project': job.project}
            if project_dict not in projects_list and job.status == 1:
                projects_list.append({'ip': node.ip, 'project': job.project})
            # for project in user.project_set.all():
            #     projects_list.append({'ip': project.node.ip, 'project': project.name})
            #     if project.node.ip in nodes_cache:
            #         scrapyd = nodes_cache[project.node.ip]
            #     else:
            #         scrapyd = scrapyd_obj(uri(project.node.ip, project.node.port))
            #         nodes_cache[project.node.ip] = scrapyd
            #
            #     if scrapyd:
            #         spiders = scrapyd.list_spiders(project.name)
            #         spiders_tmp_list = [{'node': project.node.nid.__str__(), 'project': project.name, 'spider': spider,
            #                              'ip': project.node.ip} for spider in spiders]
            #         spiders_list.extend(spiders_tmp_list)
            #
            #         # for job in spiders_list:
            #         #     Job.objects.create(name=job['spider'], project=project, user=user)

        result['data'] = {}
        result['data']['pages'] = get_pages(len(spiders_list), per)
        page = result['data']['pages'] if page >= result['data']['pages'] else page
        result['data']['spiders'] = spiders_list[(page - 1) * per:page * per]
        result['data']['projects'] = projects_list

        return Response(result)

    def post(self, request):
        result = {'status': 1, 'msg': None, 'data': None}
        per = 10
        # 处理过滤条件
        demo = {'node': 'node__ip', 'project': 'name', 'status': 'status'}
        tmp = request.POST.dict()
        page = int(tmp.pop('page'))
        status = int(tmp.pop('status'))
        condition = {demo[k]: v for k, v in tmp.items() if v not in ('0', '1', '9')}

        spiders_list = []
        user = User.objects.get(username=request.session['username'])
        # 过滤工程
        for project in user.project_set.filter(**condition):
            job_condition = {'project': project.name, 'user': user}
            if status in (0, 1): job_condition['status'] = status
            # 过滤作业
            job_set = Job.objects.filter(**job_condition)

            for job in job_set:
                if job.status == 1:
                    spiders_list.append(
                        {'node': project.node.nid.__str__(), 'project': project.name, 'spider': job.name,
                         'ip': project.node.ip})

        result['data'] = {}
        result['data']['pages'] = get_pages(len(spiders_list), per)
        page = result['data']['pages'] if page >= result['data']['pages'] else page
        result['data']['spiders'] = spiders_list[(page - 1) * per:page * per]
        # result['data']['projects'] = projects_list

        return Response(result)


@api_view(['GET', 'POST'])
def project_upload(request):
    # 工程部署
    result = {'status': 1, 'msg': None, 'data': None}

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
            # 部署之前删除之前的zip文件
            if tmp.file and os.path.exists(tmp.file.path):
                os.remove(tmp.file.path)
            else:
                os.remove(settings.MEDIA_ROOT + '/deploy/%s.zip' % tmp.name)
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

    return Response(result)


@api_view(['POST'])
def project_mapping(request):
    # 映射scrapyd的工程到记录表中
    result = {'status': 1, 'msg': None, 'data': None}
    if request.method == 'POST':
        user = User.objects.get(username=request.session['username'])
        node = Node.objects.get(nid=request.POST.get('nid'))
        projects = request.POST.get('projects').split(',')

        scrapyd = scrapyd_obj(uri(node.ip, node.port))
        if scrapyd:
            # 删除未部署的记录
            for project in set(projects) - set(scrapyd.list_projects()):
                if project:
                    # 删除工程
                    project_obj = Project.objects.get(name=project, node=node, user=user)
                    project_obj.delete()
                    # 删除作业
                    job_obj = Job.objects.filter(project=project, node=node.nid, user=user)
                    job_obj.delete()

            # 映射部署到记录表
            for project in scrapyd.list_projects():
                Project.objects.get_or_create(name=project, node=node, user=user)

    result['msg'] = '映射执行成功！'

    return Response(result)


@api_view(['POST'])
def job_mapping(request):
    # 修改爬虫状态
    result = {'status': 1, 'msg': None, 'data': None}
    if request.method == 'POST':
        user = User.objects.get(username=request.session['username'])
        node = Node.objects.get(nid=request.POST.get('nid'))
        project = Project.objects.get(pk=request.POST.get('id'))
        status = request.POST.get('status')
        scrapyd = scrapyd_obj(uri(node.ip, node.port))
        if scrapyd:
            spiders_list = scrapyd.list_spiders(project.name)
            for spider in spiders_list:
                job = Job.objects.get_or_create(name=spider, project=project.name, user=user, node=project.node.nid)
                job[0].status = status
                job[0].save()

            project.status = status
            project.save()
            result['msg'] = '修改成功！'
    return Response(result)


@api_view(['GET', 'POST'])
def job_start(request):
    # 启动爬虫
    result = {}
    if request.method == 'POST':
        data = request.POST.dict()
        nid, project, spider = data['data'].split(',')

        node = Node.objects.get(nid=nid)
        scrapyd = scrapyd_obj(uri(node.ip, node.port))
        if scrapyd:
            result['job'] = scrapyd.schedule(project, spider)
        result['node'] = nid
        result['project'] = project
        result['spider'] = spider
        return Response(result)


@api_view(['GET', 'POST'])
def job_stop(request):
    # 停止爬虫
    def _is_alive(scrapyd, project, jid):
        for job in scrapyd.list_jobs(project)['running']:
            if job['id'] == jid:
                return True

    result = {}
    if request.method == 'POST':
        data = request.POST.dict()
        nid, project, jid, spider = data['data'].split(',')
        node = Node.objects.get(nid=nid)
        scrapyd = scrapyd_obj(uri(node.ip, node.port))
        if scrapyd:
            scrapyd.cancel(project, jid)

            # 强制停止
            if _is_alive(scrapyd, project, jid):
                scrapyd.cancel(project, jid, 'KILL')

        result['node'] = nid
        result['project'] = project
        result['spider'] = spider

        return Response(result)


@api_view(['GET', 'POST'])
def job_status(request):
    # def _is_alive(scrapyd, project, jid):
    #     for job in scrapyd.list_jobs(project)['running']:
    #         if job['id'] == jid:
    #             return True
    #
    # data = request.POST.dict()
    # nid, project, jid, spider = data['data'].split(',')
    # node = Node.objects.get(nid=nid)
    # scrapyd = scrapyd_obj(uri(node.ip, node.port))
    # if scrapyd:
    #     if _is_alive(scrapyd, project, jid):
    #         return

    return Response()


@api_view(['GET', 'POST'])
def job_view(request):
    # 查看作业
    result = {}
    if request.method == 'POST':
        data = request.POST.dict()
        nid, project, spider = data['data'].split(',')
        node = Node.objects.get(nid=nid)
        scrapyd = scrapyd_obj(uri(node.ip, node.port))
        if scrapyd:
            jobs = scrapyd.list_jobs(project)

            spiders_list = []
            for status, job in jobs.items():
                if status == 'node_name': continue
                for j in job:
                    if j['spider'] == spider:
                        j['start_time'] = j['start_time'][:19] if 'start_time' in j else ''
                        j['end_time'] = j['end_time'][:19] if 'end_time' in j else ''
                        spiders_list.append(j)
            result['spiders'] = spiders_list
            result['project'] = project
            result['node'] = node.ip
            result['port'] = node.port
            result['nid'] = node.nid
            return Response(result)


@api_view(['GET', 'POST'])
def log_view(request):
    result = {'status': 1, 'msg': None, 'data': None}
    data = request.GET.dict()
    node = Node.objects.get(nid=data['nid'])
    url = uri(node.ip, node.port) + '/logs/%s/%s/%s.log' % (data['project'], data['spider'], data['job'])
    head = requests.head(url)
    length = int(head.headers['Content-Length'])
    length = length if length < 10240 else 10240
    response = requests.get(url, headers={'Range': 'bytes=-%s' % length})
    txt = response.content.decode().split('\n')[-100:]
    result['data'] = ''.join(txt)
    return Response(result)
