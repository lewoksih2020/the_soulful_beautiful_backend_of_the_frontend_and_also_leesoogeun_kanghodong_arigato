from django.core.management.base import BaseCommand, CommandError
import random

from comments.factory import CommentFactory
from comments.models import Comment
from redditors.models import User
from loanrequests.models import Loanrequest
    
class Command(BaseCommand):
    help="Adds fake comments to the database"
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--number_roots',
            '-r',
            type=int,
            default=0,
            help='Number of root comments to create'
        )
        
        parser.add_argument(
            '--number_children',
            '-c',
            type=int,
            default=0,
            help='Number of child comments to create'
        )
        
    def handle(self,*args, **options):
        n_roots = options['number_roots']
        n_children = options['number_children']

        users = User.objects.all()
        loanrequests = Loanrequest.objects.all()
        comments = Comment.objects.all()
        
        if n_roots:
            out = "Creating {} new root comments".format(n_roots)
            self.stdout.write(out)
            for _ in range(n_roots):
                authorsender = random.choice(users)
                loanrequest = random.choice(loanrequests)
                comment = CommentFactory.create(authorsender=authorsender, loanrequest=loanrequest)
                self.stdout.write("\t-- Body: {} ...".format(comment.body[0:10]))
                
        if n_children:
            out = "Creating {} new child comments".format(n_children)
            self.stdout.write(out)
            for _ in range(n_children):
                authorsender = random.choice(users)
                parent = random.choice(comments)
                loanrequest = Loanrequest.objects.get(pk=parent.loanrequest_id)
                comment = CommentFactory.create(
                    authorsender=authorsender,
                    parent=parent,
                    loanrequest=loanrequest
                )
                self.stdout.write("\t-- Body: {} ...".format(comment.body[0:10]))
