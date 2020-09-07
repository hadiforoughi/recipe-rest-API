from rest_framework import serializers
from core.models import Tag, Ingredient, Recipe

class TagSerializer(serializers.ModelSerializer):
    """serializer for tag objects"""

    class Meta:
        model = Tag
        fields = ('id','name')
        read_only_fields = ('id',)


class IngredientSerializer(serializers.ModelSerializer):
    """serializer for ingredient objects"""

    class Meta:
        model = Ingredient
        fields = ('id','name')
        read_only_fields = ('id',)

class RecipeSerializer(serializers.ModelSerializer):
    """serializer for recipe objects"""

    class Meta:
        model = Recipe
        fields = ('id','title','ingredient','tag','time_minutes','price','link')
        read_only_fields = ('id',)


class RecipeDetailSerializer(RecipeSerializer):
    tag = IngredientSerializer(many=True,read_only=True)
    ingredient = IngredientSerializer(many=True,read_only=True)