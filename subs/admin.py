from django.contrib import admin
from import_export.admin import ImportExportModelAdmin

from log import setup_logger
from subs.models import Sub

logger = setup_logger()

hell = [field.name for field in Sub._meta.get_fields()]
logger.info(hell)

@admin.register(Sub)
class SubAdmin(ImportExportModelAdmin):
    pass
