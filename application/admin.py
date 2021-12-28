# Register your models here.
from django.contrib import admin
from django.contrib.admin.views.decorators import staff_member_required
# from django.contrib.sites import admin
# from django.contrib.auth import admin
from django.db.models import QuerySet
from rest_framework import status
from rest_framework.response import Response

from application.models import Crpto1


@admin.register(Crpto1)
class CrptoAdmin(admin.ModelAdmin):
    list_display = ["x","name","wazix","coindcx"]

    def get_queryset(self, request):
        crpto = Crpto1()
        crpto.name = "BTC"
        crpto.wazix= "5USDT"
        crpto.coindcx ="10USDT"
        return QuerySet()

    def get_fields(self, request, obj=None):
        return self.list_display

admin.site.registe(Crpto1, CrptoAdmin)