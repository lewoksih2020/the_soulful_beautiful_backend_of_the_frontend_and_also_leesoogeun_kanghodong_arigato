from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from subs.models import Sub
from .models import User, UserSubMembership


class UserSerializer(serializers.ModelSerializer):
    subs = serializers.SlugRelatedField(
        many=True,
        read_only=True,
        slug_field='title',

    )

    moderated_subs = serializers.SlugRelatedField(
        many=True,
        read_only=True,
        slug_field='title',

    )

    dummySubResponse = ""

    class Meta:
        model = User
        fields = ('pk', 'karma', 'username', 'subs', 'location', 'first_name', 'last_name', 'age', 'moderated_subs', 'dummySubResponse',)


class UserCreateSerializer(serializers.ModelSerializer):
    username = serializers.SlugField(
        max_length=128,
        min_length=4,
        required=True,
        help_text=_(
            'Required, 4-128 characters, only letters, numbers, underscores and hyphens.'
        ),
        validators=[
            UniqueValidator(
                queryset=User.objects.all(),
                message="This username is already in use."
            )
        ]
    )

    location = serializers.SlugField(
        max_length=128,
        min_length=1,
        required=True,
        help_text=_(
            'Required location, 4-128 characters, only letters, numbers, underscores and hyphens.'
        ),
    )

    first_name = serializers.SlugField(
        max_length=128,
        min_length=1,
        required=True,
        help_text=_(
            'Required first_name, 4-128 characters, only letters'
        ),
    )

    last_name = serializers.SlugField(
        max_length=128,
        min_length=1,
        required=True,
        help_text=_(
            'Required last_name, 4-128 characters, only letters'
        ),
    )

    age = serializers.SlugField(
        max_length=128,
        min_length=1,
        required=True,
        help_text=_(
            'Required age, 4-128 characters, only numbers'
        ),
    )

    password = serializers.CharField(
        max_length=128, min_length=6, write_only=True, required=True,
        help_text=_('Required, 6-128 characters')
    )

    email = serializers.EmailField(
        required=True,
        validators=[UniqueValidator(
            queryset=User.objects.all(),
            message="This email is already in use."
        )]
    )

    subs = serializers.HyperlinkedRelatedField(
        required=False,
        many=True,
        queryset=Sub.objects.all(),
        view_name="sub-detail"
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'location', 'first_name', 'last_name', 'age', 'password', 'subs']

    def create(self, validated_data):
        user = User(
            email=validated_data['email'],
            username=validated_data['username'],
            location=validated_data['location'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            age=validated_data['age']
        )
        user.set_password(validated_data['password'])
        user.save()

        if validated_data.get('subs'):
            for sub in validated_data['subs']:
                UserSubMembership.objects.get_or_create(user=user, sub=sub)

        return user


class UserUpdateSerializer(serializers.ModelSerializer):
    """
    Currently only used to update user password and/or email.
    No email verification is currently included, other than
    a check for uniqueness. Whatever they change they must
    provide their current password in addition to being
    already otherwise authenticated.
    """

    current_password = serializers.CharField(
        max_length=128,
        min_length=6,
        write_only=True,
        required=True,
        help_text=_('Required, 6-128 characters')
    )

    new_password = serializers.CharField(
        max_length=128,
        min_length=6,
        write_only=True,
        required=False,
        allow_null=True,
        allow_blank=True,
    )

    email = serializers.EmailField(
        validators=[
            UniqueValidator(
                queryset=User.objects.all(),
                message="Sorry! This email is already in use."
            )
        ],
        required=False,
        allow_null=True,
        allow_blank=True,
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'location', 'first_name', 'last_name', 'age', 'current_password', 'new_password']
        lookup_field = 'username'

    def update(self, instance, validated_data):
        try:
            user = self.context.get('request').user
        except:
            message = _("You must be logged in to make profile changes.")
            raise serializers.ValidationError(message)

        try:
            current_password = validated_data.pop('current_password')
        except KeyError:
            message = _("Please enter your current password.")
            raise serializers.ValidationError(message)

        if not user.check_password(current_password):
            message = _("Please enter your current password")
            raise serializers.ValidationError(message)

        if validated_data.get("new_password"):
            new_password = validated_data.pop("new_password")
            if new_password == current_password:
                message = _("Your new password can not be set the to the "
                            "same value as your current password")
                raise serializers.ValidationError(message)
            user.set_password(new_password)

        if validated_data.get("email"):
            user.email = validated_data['email']
        print(validated_data.get("email"))
        user.save()

        return user


# from comments.serializers import CommentSerializer
from loanrequests.serializers import LoanrequestSerializer

from savingrequests.serializers import SavingrequestSerializer

class UserProfileSerializer(serializers.ModelSerializer):
    """
    Provide the detail of a user, not for login but for profile pages.
    All information provied here will be publicly accessable.
    """
    # subs = serializers.PrimaryKeyRelatedField(
    #     many=True,
    #     read_only=True,
    # )
    subs = serializers.SlugRelatedField(
        many=True,
        read_only=True,
        slug_field='title'

    )
    # moderated_subs = serializers.PrimaryKeyRelatedField(
    #     many=True,
    #     read_only=True,
    # )

    moderated_subs = serializers.SlugRelatedField(
        many=True,
        read_only=True,
        slug_field='title'

    )
    cake_day = serializers.DateTimeField(
        source='date_joined'
    )
    # comments = serializers.SerializerMethodField()
    loanrequests = serializers.SerializerMethodField()
    savingrequests = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'pk',
            'username',
            'email',
            'subs',
            'first_name',
            'last_name',
            'age',
            'moderated_subs',
            'location',
            'loanrequests',
            'savingrequests',

            'karma',
            'cake_day'
        )

    # def get_comments(self, obj):
    #     serializer = CommentSerializer(
    #         obj.comments.all().order_by("-created"),
    #         many=True,
    #         context=self.context
    #     )
    #     return serializer.data

    def get_loanrequests(self, obj):
        serializer = LoanrequestSerializer(
            obj.loanrequests.all().order_by("-created"),
            many=True,
            context=self.context
        )
        return serializer.data

    def get_savingrequests(self, obj):
        serializer = SavingrequestSerializer(
            obj.savingrequests.all().order_by("-created"),
            many=True,
            context=self.context
        )
        return serializer.data

    # def get_subs(self, obj):
    #     serializer = SubSerializer(
    #         obj.subs.all(),
    #         many=True,
    #         context=self.context
    #     )
    #     return serializer.data


class AccountPropertiesSerializer(serializers.ModelSerializer):
    subs = serializers.SlugRelatedField(
        many=True,
        read_only=True,
        slug_field='title'

    )
    # moderated_subs = serializers.PrimaryKeyRelatedField(
    #     many=True,
    #     read_only=True,
    # )

    moderated_subs = serializers.SlugRelatedField(
        many=True,
        read_only=True,
        slug_field='title'

    )
    cake_day = serializers.DateTimeField(
        source='date_joined'
    )
    # comments = serializers.SerializerMethodField()
    loanrequests = serializers.SerializerMethodField()
    savingrequests = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'pk',
            'location',
            'first_name',
            'last_name',
            'age',
            'username',
            'email',
            'subs',
            'moderated_subs',
            'loanrequests',
            'savingrequests',
            'karma',
            'cake_day'
        )

    # def get_comments(self, obj):
    #     serializer = CommentSerializer(
    #         obj.comments.all().order_by("-created"),
    #         many=True,
    #         context=self.context
    #     )
    #     return serializer.data

    def get_loanrequests(self, obj):
        serializer = LoanrequestSerializer(
            obj.loanrequests.all().order_by("-created"),
            many=True,
            context=self.context
        )
        return serializer.data

    def get_savingrequests(self, obj):
        serializer = SavingrequestSerializer(
            obj.savingrequests.all().order_by("-created"),
            many=True,
            context=self.context
        )
        return serializer.data

    # class Meta:
    #     model = User
    #     fields = ['pk', 'email', 'username', ]
