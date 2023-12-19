from django.contrib import admin

from .models import Census
from .models import CensusGroup
from .models import CensusImport


class CensusAdmin(admin.ModelAdmin):
    list_display = ('voting_id', 'voter_id')
    list_filter = ('voting_id', )

    search_fields = ('voter_id', )


class CensusGroupAdmin(admin.ModelAdmin):
    list_display = ('name', )
    search_fields = ('name', )


class CensusImportAdmin(admin.ModelAdmin):
    list_display = ('file', )


admin.site.register(Census, CensusAdmin)
admin.site.register(CensusGroup, CensusGroupAdmin)
admin.site.register(CensusImport, CensusImportAdmin)