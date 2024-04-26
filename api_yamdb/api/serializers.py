from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator


from reviews.models import Title, Genre, Category, MyUser, Review, Comment


class MyUserSerializer(serializers.ModelSerializer):

    class Meta:
        model = MyUser
        fields = (
            'username', 'email', 'first_name', 'last_name', 'bio', 'role',
        )


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
