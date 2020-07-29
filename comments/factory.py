import factory
import random
import faker
from django.utils import timezone

from comments.models import Comment


class CommentFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Comment

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        fake = faker.Faker()
        comment_length = max(
            round(random.betavariate(1.5, 3) * 3000),
            10
        )
        kwargs['body'] = fake.text(comment_length)
        return super()._create(model_class, *args, **kwargs)

    created = factory.Faker(
        'date_time_between',
        start_date="-12m",
        end_date="now",
        tzinfo=timezone.utc
    )
