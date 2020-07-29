from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework.test import APIClient
from django.core.exceptions import ValidationError

from redditors.models import User, UserSubMembership
from subs.models import Sub
from loanrequests.models import Loanrequest
from votes.models import LoanrequestVote

class LoanrequestTest(APITestCase):
    """
    General post creation without a request
    """
    def setUp(self):
        # need a subreddit
        self.subreddit = Sub.objects.create(
            title='test_subreddit'
        )

        # and a user
        self.user_data = {
            'username': 'test_username',
            'email': 'test@gmail.com',
            'password': 'test_password',
            }
        self.user = User.objects.create(**self.user_data)
        self.user_data_2 = {
            'username': 'test_username_2',
            'email': 'test2@gmail.com',
            'password': 'test_password',
            }
        self.user2 = User.objects.create(**self.user_data_2)
        
        self.loanrequest_data = {
            "title": "test loanrequest_title",
            "body": "Test loanrequest body",
        }
        
    def test_loanrequest_creation(self):
        """
        Can create a post with a subreddit and a user
        """
        loanrequest = Loanrequest.objects.create(
            subreddit=self.subreddit,
            authorsender=self.user,
            **self.loanrequest_data
        )
        self.assertEqual(Loanrequest.objects.count(), 1)
        self.assertIs(loanrequest.authorsender, self.user)
        self.assertIs(loanrequest.subreddit, self.subreddit)
        self.assertEqual(loanrequest.title, self.loanrequest_data["title"])
        self.assertEqual(loanrequest.body, self.loanrequest_data["body"])
        
    def test_loanrequest_creation_long_title(self):
        """
        The maximum title length is 150 chars
        """
        error_message = "The title can only be 150 characters in length."
        with self.assertRaises(ValidationError):
            loanrequest = Loanrequest(
                subreddit=self.subreddit,
                authorsender=self.user,
                title = 'a'*151,
                body = "test body"
            )
            loanrequest.full_clean()
        
class LoanrequestRequestTests(APITestCase):
    """
    Testing request for making, updating and deleting loanrequests
    """
    def setUp(self):
        # need a subreddit
        self.subreddit = Sub.objects.create(
            title='test_subreddit'
        )

        # and a user
        self.user_data = {
            'username': 'test_username',
            'email': 'test@gmail.com',
            'password': 'test_password',
            }
        self.user = User.objects.create(**self.user_data)
        self.user_data_2 = {
            'username': 'test_username_2',
            'email': 'test2@gmail.com',
            'password': 'test_password',
            }
        self.user2 = User.objects.create(**self.user_data_2)
        

        self.client.force_login(self.user)
        
        self.create_loanrequest_url_f = lambda title: reverse(
            'create-loanrequest',
            kwargs={ "sub_title": title}
        )
        self.create_loanrequest_url = reverse(
            'create-loanrequest',
            kwargs={ "sub_title": self.subreddit.title}
        )
        self.detail_loanrequest_url = lambda pk: reverse(
            'loanrequest-detail',
            kwargs={ "pk": pk}
        )
        self.loanrequest_data = {
            "title": "test loanrequest_title",
            "body": "Test loanrequest body",
        }
        
    
        
    def test_create_loanrequest_non_member(self):
        """
        Can't create a post to a subreddit without a subreddit membership
        """
        response = self.client.post(self.create_loanrequest_url, self.loanrequest_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Loanrequest.objects.count(), 0)
        self.assertEqual(self.subreddit.loanrequests.count(), 0)
        self.assertEqual(self.user.loanrequests.count(), 0)
        self.assertContains(
            response,
            "You must be a member of the subreddit to post here.",
            status_code=400
        )
        
    def test_create_loanrequest_member(self):
        """
        A member of a subreddit can create a post there
        """
        UserSubMembership.objects.create(
            user=self.user,
            sub=self.subreddit
        )
        response = self.client.post(self.create_loanrequest_url, self.loanrequest_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Loanrequest.objects.count(), 1)
        self.assertEqual(self.subreddit.loanrequests.count(), 1)
        self.assertEqual(self.user.loanrequests.count(), 1)
        self.assertNotIn(response.data["pk"], self.user.loanrequests.all())
        self.assertNotIn(response.data["pk"], self.subreddit.loanrequests.all())
        self.assertEqual(response.data["subreddit"], self.subreddit.pk)
        self.assertEqual(response.data["subreddit_title"], self.subreddit.title)
        self.assertEqual(response.data["authorsender"], self.user.pk)
        self.assertEqual(response.data["authorsender_username"], self.user.username)
        
    def test_loanrequest_creation_psuedo_subreddit(self):
        """
        Should not be able to post to All, Popular, or Home subreddits
        """
        pseudo_names = ["Home", "home", "hOme", "Popular", "All"]
        for title in pseudo_names:
            response = self.client.post(
                self.create_loanrequest_url_f(title),
                self.loanrequest_data
            )
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertEqual(Loanrequest.objects.count(), 0)
        
    def test_loanrequest_update_authorsender(self):
        """
        The creator of a post can update it
        """
        UserSubMembership.objects.create(
            user=self.user,
            sub=self.subreddit
        )
        loanrequest = Loanrequest.objects.create(
            subreddit=self.subreddit,
            authorsender=self.user,
            **self.loanrequest_data
        )
        
        self.assertEqual(Loanrequest.objects.count(), 1)
        update_data = {
         "body": "new body"
        }
        response = self.client.patch(self.detail_loanrequest_url(loanrequest.pk), update_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Loanrequest.objects.count(), 1)
        self.assertEqual(response.data["body"], update_data["body"])
        
    def test_loanrequest_update_non_authorsender(self):
        """
        The if you didn't create the post you can't update
        unless your a moderator
        """
        UserSubMembership.objects.create(
            user=self.user2,
            sub=self.subreddit
        )
        loanrequest = Loanrequest.objects.create(
            subreddit=self.subreddit,
            authorsender=self.user2,
            **self.loanrequest_data
        )
        update_data = {
         "body": "new body"
        }
        response = self.client.patch(self.detail_loanrequest_url(loanrequest.pk), update_data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
        # make user a moderator
        self.subreddit.moderators.add(self.user)
        response = self.client.patch(self.detail_loanrequest_url(loanrequest.pk), update_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Loanrequest.objects.count(), 1)
        self.assertEqual(response.data["body"], update_data["body"])
        
        
    def test_loanrequest_delete_authorsender(self):
        """
        The creator of a post can delete it
        """
        UserSubMembership.objects.create(
            user=self.user,
            sub=self.subreddit
        )
        loanrequest = Loanrequest.objects.create(
            subreddit=self.subreddit,
            authorsender=self.user,
            **self.loanrequest_data
        )
        
        self.assertEqual(Loanrequest.objects.count(), 1)
        response = self.client.delete(self.detail_loanrequest_url(loanrequest.pk))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Loanrequest.objects.count(), 0)
        
    def test_loanrequest_delete_non_authorsender(self):
        """
        A user who did not create the post can't delete it
        unless they are a moderator of the subreddit
        """
        UserSubMembership.objects.create(
            user=self.user2,
            sub=self.subreddit
        )
        loanrequest = Loanrequest.objects.create(
            subreddit=self.subreddit,
            authorsender=self.user2,
            **self.loanrequest_data
        )
        
        self.assertEqual(Loanrequest.objects.count(), 1)
        response = self.client.delete(self.detail_loanrequest_url(loanrequest.pk))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Loanrequest.objects.count(), 1)
        
        # make user a moderator
        self.subreddit.moderators.add(self.user)
        response = self.client.delete(self.detail_loanrequest_url(loanrequest.pk))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Loanrequest.objects.count(), 0)
        
        
class LoanrequestRetrieveRequestTests(APITestCase):
    """
    Testing request for retrieving lists of loanrequests, including
    pseudo-subreddits and pagination
    """
    def setUp(self):
        # need a subreddit
        self.subreddit = Sub.objects.create(
            title='test_subreddit'
        )

        # and a user or two
        self.user_data = {
            'username': 'test_username',
            'email': 'test@gmail.com',
            'password': 'test_password',
            }
        self.user = User.objects.create(**self.user_data)
        self.user_data_2 = {
            'username': 'test_username_2',
            'email': 'test2@gmail.com',
            'password': 'test_password',
            }
        self.user2 = User.objects.create(**self.user_data_2)
        
        for loanrequest_num in range(10):
            Loanrequest.objects.create(
                authorsender=self.user,
                subreddit=self.subreddit,
                title="user_1_loanrequest_title_{}".format(loanrequest_num)
            )
        for loanrequest_num in range(10):
            Loanrequest.objects.create(
                authorsender=self.user2,
                subreddit=self.subreddit,
                title="user_2_loanrequest_title_{}".format(loanrequest_num)
            )
        
        self.sub_loanrequest_list_url = reverse(
            'sub-loanrequest-list',
            kwargs={ "sub_title": self.subreddit.title}
        )
        self.sub_loanrequest_list_url_f = lambda title: reverse(
            'sub-loanrequest-list',
            kwargs={ "sub_title": title}
        )

    def test_real_subreddit_retrieval(self):
        """
        An unauthed user can retrive all of the loanrequests from a particular
        subreddit.
        """
        response = self.client.get(self.sub_loanrequest_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertContains(response, "user_1_loanrequest_title_", count=10)
        self.assertContains(response, "user_2_loanrequest_title_", count=10)
        
    def test_real_non_subreddit_retrieval(self):
        """
        A request for the loanrequests of a subreddit that doesn't exist
        raises a 404
        """
        response = self.client.get(self.sub_loanrequest_list_url_f("non_sub"))
        self.assertContains(
            response,
            "The 'non_sub' subreddit does not exist",
            count=1,
            status_code=404
        )
        
    def test_pseudo_home_subreddit_retrieval(self):
        """
        An unauthed request to the 'Home' psuedo subReddit returns
        a list of all of the loanrequests
        """
        response = self.client.get(self.sub_loanrequest_list_url_f("Home"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertContains(response, "user_1_loanrequest_title_", count=10)
        self.assertContains(response, "user_2_loanrequest_title_", count=10)
        
    def test_auth_pseudo_home_subreddit_retrieval(self):
        """
        An authenticated request to the 'Home' psuedo subReddit returns
        a list of all of the loanrequests for the subreddits the user is subcribed to
        """
        self.client.force_login(self.user)
        # create a new subreddit for this test
        self.subreddit2 = Sub.objects.create(
            title='test_subreddit_2'
        )
        # sign up for the subreddit
        UserSubMembership.objects.create(
            user=self.user,
            sub=self.subreddit2
        )
        # make some loanrequests in new subreddit
        for loanrequest_num in range(10):
            Loanrequest.objects.create(
                authorsender=self.user,
                subreddit=self.subreddit2,
                title="these_are_in_sub2_{}".format(loanrequest_num)
            )
        response = self.client.get(self.sub_loanrequest_list_url_f("Home"))
        self.assertContains(
            response,
            "these_are_in_sub2_",
            count=10
        )
        self.assertNotContains(response, "user_1_loanrequest_title_")
        self.assertNotContains(response, "user_2_loanrequest_title_")
        
    def test_pseudo_popular_subreddit_retrieval(self):
        """
        Should only return the popular loanrequests, at this point that
        means loanrequests with more than on upvote.
        """
        # pick half of the 20 loanrequests we made in setUp to become popular
        evens = range(0,10,2)
        for loanrequest in Loanrequest.objects.all():
            if int(loanrequest.title[-1]) in evens:
                LoanrequestVote.objects.create(
                    loanrequest=loanrequest,
                    user=self.user,
                    vote_type=1
                )
                LoanrequestVote.objects.create(
                    loanrequest=loanrequest,
                    user=self.user2,
                    vote_type=1
                )
        
        response = self.client.get(self.sub_loanrequest_list_url_f("Popular"))
        self.assertContains(response, "user_1_loanrequest_title_", count=5)
        self.assertContains(response, "user_2_loanrequest_title_", count=5)
        self.assertNotContains(response, "user_1_loanrequest_title_1")
        self.assertNotContains(response, "user_2_loanrequest_title_3")
        
    def test_pseudo_all_subreddit_retrieval(self):
        """
        Should only return the all loanrequests, at this point that
        means loanrequests with more than on upvote.
        NOTE: at this point the all subreddit is identical to the
        popular subreddit so this test is also identical
        """
        # pick half of the 20 loanrequests we made in setUp to become popular
        evens = range(1,11,2)
        for loanrequest in Loanrequest.objects.all():
            if int(loanrequest.title[-1]) in evens:
                LoanrequestVote.objects.create(
                    loanrequest=loanrequest,
                    user=self.user,
                    vote_type=1
                )
                LoanrequestVote.objects.create(
                    loanrequest=loanrequest,
                    user=self.user2,
                    vote_type=1
                )
        
        response = self.client.get(self.sub_loanrequest_list_url_f("All"))
        self.assertContains(response, "user_1_loanrequest_title_", count=5)
        self.assertContains(response, "user_2_loanrequest_title_", count=5)
        self.assertNotContains(response, "user_1_loanrequest_title_0")
        self.assertNotContains(response, "user_2_loanrequest_title_2")
        
    def test_pagination(self):
        """
        requests can specify limit and offset GET query parameters to
        indicate pagination requirements
        """
        # make some more loanrequests
        for loanrequest_num in range(10):
            Loanrequest.objects.create(
                authorsender=self.user,
                subreddit=self.subreddit,
                title="pagination_user_1_loanrequest_title_{}".format(loanrequest_num)
            )

        pagination_parameters = {
            'offset': 0,
            'limit': 5
        }
        response = self.client.get(self.sub_loanrequest_list_url, pagination_parameters)
        self.assertContains(response, "user_1_loanrequest_title_", count=5)
        self.assertNotContains(response, "user_2_loanrequest_title_")
        
        pagination_parameters = {
            'offset': 5,
            'limit': 10
        }
        response = self.client.get(self.sub_loanrequest_list_url, pagination_parameters)
        self.assertContains(response, "user_1_loanrequest_title_", count=5)
        self.assertContains(response, "user_2_loanrequest_title_", count=5)
        
        pagination_parameters = {
            'offset': 15,
            'limit': 5
        }
        response = self.client.get(self.sub_loanrequest_list_url, pagination_parameters)
        self.assertContains(response, "user_2_loanrequest_title_", count=5)
        self.assertNotContains(response, "user_1_loanrequest_title_")

    def test_pagination_next(self):
        """
        The pagination response contains a 'next' hyperlink that can
        be followed to retrieve the next set.
        """
        pagination_parameters = {
            'offset': 0,
            'limit': 10
        }
        response = self.client.get(self.sub_loanrequest_list_url, pagination_parameters)
        response = self.client.get(response.data["next"])
        self.assertContains(response, "user_2_loanrequest_title_", count=10)
        self.assertNotContains(response, "user_1_loanrequest_title_")
        
    def test_pagination_next_with_orderby(self):
        """
        The orderby query parameter should be preserved to the
        'next' hyperlink of the pagination response. And the ordering
        should still work.
        """
        # make half of the loanrequests popular
        evens = range(1,11,2)
        for loanrequest in Loanrequest.objects.all():
            if int(loanrequest.title[-1]) in evens:
                LoanrequestVote.objects.create(
                    loanrequest=loanrequest,
                    user=self.user,
                    vote_type=1
                )
                LoanrequestVote.objects.create(
                    loanrequest=loanrequest,
                    user=self.user2,
                    vote_type=1
                )
                        
        pagination_parameters = {
            'offset': 0,
            'limit': 10
        }
        q_params = {
            **pagination_parameters,
            "orderby": "popular"
        }
        response = self.client.get(self.sub_loanrequest_list_url_f("Home"), q_params)
        self.assertContains(response, "user_1_loanrequest_title_", count=5)
        self.assertContains(response, "user_2_loanrequest_title_", count=5)
        self.assertIn("orderby=popular", response.data["next"])
        # make sure they were all the popular ones
        popularity = []
        for loanrequest in response.data["results"]:
            popularity.append(loanrequest["upvotes"]==2)
        self.assertTrue(all(popularity))
        
        # now make sure these are the unpopular ones
        response = self.client.get(response.data["next"])
        popularity = []
        for loanrequest in response.data["results"]:
            popularity.append(loanrequest["upvotes"]==0)
        self.assertTrue(all(popularity))
        
        
