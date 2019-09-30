from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User

import uuid


class Node(models.Model):
    '''节点'''
    nid = models.UUIDField(default=uuid.uuid4, primary_key=True, null=False)
    name = models.CharField(max_length=255, default=None)
    ip = models.GenericIPAddressField(null=True, blank=True, unique=True)
    port = models.IntegerField(default=6800, blank=True, null=True)
    status = models.IntegerField(default=1, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    platform = models.CharField(max_length=255, default=None)

    # 认证
    username = models.CharField(max_length=255, blank=True, null=True)
    password = models.CharField(max_length=255, blank=True, null=True)

    add_date = models.DateTimeField(auto_now_add=True)
    update_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'Node'


class Project(models.Model):
    '''工程列表'''
    user = models.ForeignKey(User, on_delete='models.CASCADE')
    name = models.CharField(max_length=128)
    file = models.FileField(upload_to='deploy')
    description = models.TextField(blank=True, null=True, default='')
    node = models.ForeignKey(Node, on_delete='models.CASCADE', default=None)
    status = models.IntegerField(default=1, blank=True, null=True)

    add_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return '<%s %s>' % (self.name, self.node.ip)

    class Meta:
        verbose_name_plural = 'Project'


class Job(models.Model):
    user = models.ForeignKey(User, on_delete='models.CASCADE')
    name = models.CharField(max_length=128)
    status = models.IntegerField(default=1, blank=True, null=True)
    description = models.TextField(blank=True, null=True, default='')
    project = models.CharField(max_length=128, default='')
    add_time = models.DateTimeField(auto_now_add=True)

    start_time = models.DateTimeField(blank=True, null=True)
    stop_time = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return '<%s %s>' % (self.name, self.project)

    class Meta:
        verbose_name_plural = 'Job'


class Deploy(models.Model):
    '''部署文件'''
    user = models.ForeignKey(User, on_delete='models.CASCADE')
    name = models.CharField(max_length=128)
    file = models.FileField(upload_to='deploy')
    address = models.CharField(max_length=520)

    def __str__(self):
        return '<%s %s>' % (self.name, self.address)

    class Meta:
        verbose_name_plural = 'Deploy'
