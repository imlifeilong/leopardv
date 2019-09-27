from rest_framework import serializers
from api.models import Node, Project


class NodeSerializer(serializers.ModelSerializer):
    '''
    节点序列化
    '''

    class Meta:
        model = Node
        fields = ('nid', 'name', 'ip', 'port', 'status', 'platform', 'description')


class ProjectSerializer(serializers.ModelSerializer):
    '''
    工程序列号
    '''
    class Meta:
        model = Project
        fields = ('id', 'name', 'address', 'description')
