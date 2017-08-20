from django.db import models
#
class Post(models.Model):
    title= models.CharField(max_length=120)
    content = models.CharField(max_length=1000)
    lastUpdate = models.DateField()
    controllerName = models.CharField(max_length=50)

