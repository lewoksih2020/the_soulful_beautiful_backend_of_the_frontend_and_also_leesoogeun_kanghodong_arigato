from django.contrib import admin
from import_export.admin import ImportExportModelAdmin

from .models import Loanrequest


# admin.site.register(Loanrequest)


@admin.register(Loanrequest)
class LoanrequestAdmin(ImportExportModelAdmin):
    pass
