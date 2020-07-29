from django.core.management.base import BaseCommand, CommandError
import random

from loanrequests.factory import LoanrequestFactory
from redditors.models import User
from subs.models import Sub
    
class Command(BaseCommand):
    help="Adds fake comments to the database"
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--number',
            '-n',
            type=int,
            default=1,
            help='Number of loanrequests to create'
        )
        
    def handle(self,*args, **options):
        n_loanrequests = options['number']
        # grab a user for each post
        users = User.objects.all().prefetch_related('subs')
        
        out = "Creating {} new loanrequests".format(n_loanrequests)
        self.stdout.write(out)
        for _ in range(n_loanrequests):
            # make sure to grab a user that has subreddit memberships
            authorsender = random.choice(users)
            while not len(authorsender.subs.all()):
                authorsender = random.choice(users)
            # assume you can only post in subreddits you are a member of
            subreddit = random.choice(authorsender.subs.all())
            loanrequest = LoanrequestFactory.create(authorsender=authorsender, subreddit=subreddit)
            self.stdout.write("\t-- Title: {} ...".format(loanrequest.title[0:10]))
