from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator
from rest_framework.validators import UniqueValidator

from reviews.models import Title, Genre, Category, MyUser, Review, Comment


class MyUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = MyUser
        fields = ('username', 'email', 'first_name',
                  'last_name', 'bio', 'role')
        extra_kwargs = {
            'username': {'required': True},
            'email': {'required': True,
                      'validators':
                      [UniqueValidator(queryset=MyUser.objects.all())]},
            'role': {'required': False},
            'confirmation_code': {'write_only': True}
        }

    def validate_email(self, value):
        if len(value) > 254:
            raise serializers.ValidationError(
                "Email must not exceed 254 characters.")
        return value

    def validate_username(self, value):
        restricted_usernames = ['me', 'admin', 'null']
        if value.lower() in restricted_usernames:
            raise serializers.ValidationError("This username is restricted and cannot be used.")
        if len(value) > 150:
            raise serializers.ValidationError("Username must not exceed 150 characters.")
        return value

    def to_representation(self, instance):
        """Modify the output data to only include fields that were in the input data."""
        ret = super().to_representation(instance)
        request = self.context.get('request')
        if request and request.method == 'POST':
            included_fields = request.data.keys()
            return {field: ret[field] for field in included_fields if field in ret}
        return ret

    def update(self, instance, validated_data):
        if 'role' in validated_data:
            if not self.context['request'].user.is_superuser:
                validated_data.pop('role', None)
        return super().update(instance, validated_data)


class TitleSerializer(serializers.ModelSerializer):
    genre = serializers.SlugRelatedField(
        queryset=Genre.objects.all(),
        many=True,
        slug_field='slug',
    )
    category = serializers.SlugRelatedField(
        queryset=Category.objects.all(),
        slug_field='slug',
    )
    # Рейтинг
    rating = 25

    class Meta:
        model = Title
        fields = (
            'id',
            'name',
            'year',
            'description',
            'rating',
            'category',
            'genre',
        )
        read_only_fields = ('id', 'rating')
        validators = [
            UniqueTogetherValidator(
                queryset=Title.objects.all(),
                fields=('name', 'year', 'category'),
            )
        ]


class GenreSerializer(serializers.ModelSerializer):

    class Meta:
        model = Genre
        fields = ('name', 'slug')


class CategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = Category
        fields = ('name', 'slug')


class ReviewSerializer(serializers.ModelSerializer):

    author = serializers.StringRelatedField(
        read_only=True
    )

    class Meta:
        model = Review
        fields = (
            'id',
            'text',
            'author',
            'score',
            'pub_date',
        )
        read_only_fields = ('id', 'title', 'author', 'pub_date')
        validators = [
            UniqueTogetherValidator(
                queryset=Title.objects.all(),
                fields=('name', 'year', 'category'),
            )
        ]


class CommentSerializer(serializers.ModelSerializer):

    author = serializers.StringRelatedField(
        read_only=True
    )

    class Meta:
        model = Comment
        fields = ("id", "text", "author", "pub_date")
        read_only_fields = ("id", "author", "pub_date")
