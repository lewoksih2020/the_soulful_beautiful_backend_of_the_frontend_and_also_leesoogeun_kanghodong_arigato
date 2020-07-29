from django.contrib import admin

from .models import CommentVote, LoanrequestVote

admin.site.register(CommentVote)
admin.site.register(LoanrequestVote)
