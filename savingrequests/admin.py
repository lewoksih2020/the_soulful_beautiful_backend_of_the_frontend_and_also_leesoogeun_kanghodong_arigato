from django.contrib import admin
from import_export.admin import ImportExportModelAdmin

from .models import Savingrequest

@admin.register(Savingrequest)
class SavingrequestAdmin(ImportExportModelAdmin):
    pass
