from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from reviews.models import Category, Comment, Genre, MyUser, Review, Title
from rest_framework.validators import UniqueValidator
from django.core.validators import MaxLengthValidator, RegexValidator
from reviews.models import MyUser
from .constants import RESTRICTED_USERNAMES


class MyUserSerializer(serializers.ModelSerializer):
    username = serializers.CharField(
        max_length=150,
        validators=[
            UniqueValidator(queryset=MyUser.objects.all()),
            MaxLengthValidator(150),
            RegexValidator(r'^[\w.@+-]+$',
                           message='Username must consist of letters,'
                           'digits, or @/./+/-/_ characters.')
        ]
    )
    email = serializers.EmailField(
        validators=[
            UniqueValidator(queryset=MyUser.objects.all()),
            MaxLengthValidator(254)
        ]
    )

    class Meta:
        model = MyUser
        fields = ('username', 'email', 'first_name',
                  'last_name', 'bio', 'role')

    def validate_username(self, value):
        if value.lower() in RESTRICTED_USERNAMES:
            raise serializers.ValidationError(
                'This username is restricted and cannot be used.')
        return value

    def to_representation(self, instance):
        representation_data = super().to_representation(instance)
        request = self.context.get('request')
        if request and request.method == 'POST':
            included_fields = request.data.keys()
            return {
                field: representation_data[field]
                for field in included_fields if field in representation_data
            }
        return representation_data

    def update(self, instance, validated_data):
        if 'role' in validated_data:
            if not self.context['request'].user.is_superuser:
                validated_data.pop('role', None)
        return super().update(instance, validated_data)



class GenreSerializer(serializers.ModelSerializer):
    """Сериализатор класса Genre."""

    class Meta:
        model = Genre
        fields = ('name', 'slug')


class CategorySerializer(serializers.ModelSerializer):
    """Сериализатор класса Category."""

    class Meta:
        model = Category
        fields = ('name', 'slug')


class TitleGetSerializer(serializers.ModelSerializer):
    """Сериализатор класса Title при GET запросах."""

    genre = GenreSerializer(many=True, read_only=True)
    category = CategorySerializer(read_only=True)
    rating = serializers.IntegerField(read_only=True)

    class Meta:
        model = Title
        fields = (
            'id',
            'name',
            'year',
            'rating',
            'description',
            'genre',
            'category'
        )


class TitleSerializer(serializers.ModelSerializer):
    """Сериализатор класса Title при небезопасных запросах."""

    genre = serializers.SlugRelatedField(
        queryset=Genre.objects.all(),
        many=True,
        slug_field='slug',
    )
    category = serializers.SlugRelatedField(
        queryset=Category.objects.all(),
        slug_field='slug',
    )

    class Meta:
        model = Title
        fields = (
            'name', 'year', 'description', 'genre', 'category')

    def to_representation(self, title):
        """Определяет какой сериализатор будет использоваться для чтения."""
        serializer = TitleGetSerializer(title)
        return serializer.data


class ReviewSerializer(serializers.ModelSerializer):
    """Сериализатор класса Review."""

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

    def validate(self, data):
        """Запрещает пользователям оставлять повторные отзывы."""

        if not self.context.get('request').method == 'POST':
            return data
        author = self.context.get('request').user
        title_id = self.context.get('view').kwargs.get('title_id')
        if Review.objects.filter(author=author, title=title_id).exists():
            raise serializers.ValidationError(
                'Вы уже оставляли отзыв на это произведение'
            )
        return data


class CommentSerializer(serializers.ModelSerializer):
    """Сериализатор класса Comment."""

    author = serializers.StringRelatedField(
        read_only=True
    )

    class Meta:
        model = Comment
        fields = ('id', 'text', 'author', 'pub_date')
        read_only_fields = ('id', 'author', 'pub_date')
