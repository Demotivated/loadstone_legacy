"""loadstone URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.8/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add an import:  from blog import urls as blog_urls
    2. Add a URL to urlpatterns:  url(r'^blog/', include(blog_urls))
"""
from django.conf.urls import include, url
from django.contrib import admin

from api.views import scrape_character_view, scrape_item_view

urlpatterns = [
    url(r'^admin/', include(admin.site.urls)),
    url(r'^scrape/character/(?P<lodestone_id>[0-9]+)/$', scrape_character_view, name='scrape_character_view'),
    url(r'^scrape/item/(?P<lodestone_id>[A-Za-z0-9]+)/$', scrape_item_view, name='scrape_item_view'),
]
