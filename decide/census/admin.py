from django.contrib import admin

from django import forms

from .models import Census
from .models import CensusGroup


class CensusAdmin(admin.ModelAdmin):
    list_display = ('voting_id', 'voter_id')
    list_filter = ('voting_id', )

    search_fields = ('voter_id', )


class CensusGroupAdmin(admin.ModelAdmin):
    list_display = ('name',)  
    search_fields = ('name',)  
  

admin.site.register(Census, CensusAdmin)
admin.site.register(CensusGroup, CensusGroupAdmin)