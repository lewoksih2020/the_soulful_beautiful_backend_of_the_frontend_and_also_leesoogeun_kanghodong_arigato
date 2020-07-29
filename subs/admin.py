from django.contrib import admin

from log import setup_logger
from subs.models import Sub

logger = setup_logger()

hell = [field.name for field in Sub._meta.get_fields()]
logger.info(hell)

admin.site.register(Sub)
