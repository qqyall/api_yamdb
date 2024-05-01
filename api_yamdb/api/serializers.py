from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from reviews.models import Category, Comment, Genre, MyUser, Review, Title


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
            raise serializers.ValidationError(
                'This username is restricted and cannot be used.')
        if len(value) > 150:
            raise serializers.ValidationError(
                'Username must not exceed 150 characters.')
        return value

    def to_representation(self, instance):
        """Modify the output data to only include
        fields that were in the input data."""

        ret = super().to_representation(instance)
        request = self.context.get('request')
        if request and request.method == 'POST':
            included_fields = request.data.keys()
            return {
                field: ret[field] for field in included_fields if field in ret}
        return ret

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
