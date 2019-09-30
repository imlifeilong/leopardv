from django.contrib import admin
from api import models

admin.site.register(models.Node)
admin.site.register(models.Project)
admin.site.register(models.Job)
