from django.db import models
#
class Post(models.Model):
    title= models.CharField(max_length=120)
    content = models.CharField(max_length=50000)
    lastUpdate = models.DateField()
    controllerName = models.CharField(max_length=50)

class Code(models.Model):
    codeID = models.IntegerField(primary_key=True)
    codeGroup= models.IntegerField()
    order = models.IntegerField()
    visible = models.BooleanField(default=True)
    title = models.CharField(max_length=500,default='New title')
    description = models.CharField(max_length=50000,default='New title')