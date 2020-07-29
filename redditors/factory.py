import factory
import random

from redditors.models import User


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        kwargs['karma'] = random.randint(0, 10000)
        django_get_or_create = ('username',)
        return super()._create(model_class, *args, **kwargs)

    username = factory.Faker('username')
    email = factory.Faker('email')
    password = 'testPassword'
