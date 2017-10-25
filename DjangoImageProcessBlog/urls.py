"""DjangoImageProcessBlog URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib.auth import views as auth_views
from django.contrib import admin

from views import views

# Uncomment the next lines to enable the admin:


urlpatterns = [
    #url(r'^admin/', admin.site.urls),
    url(r'^$', views.home),
    url(r'^home', views.home),
    url(r'^ImageProcessing', views.ImageProcessing),
    url(r'^Contact', views.Contact),
    url(r'^DigitRec', views.DigitRec),
    url(r'^simple_upload', views.simple_upload),
    url(r'^Cmfd', views.cmfd),
    url(r'^ImageRetrieval', views.ImageRetrieval),
    url(r'^login/$', auth_views.login, name='login'),
    url(r'^logout/$', auth_views.logout, name='logout'),
    url(r'^admin/', admin.site.urls),
    url(r'^GetPost', views.GetPost),
    url(r'^PanoramaCreator', views.PanoramaCreator),
    url(r'^PostEntry', views.PostEntry),
    url(r'^EmotionRecognition', views.EmotionRecognition)
]
