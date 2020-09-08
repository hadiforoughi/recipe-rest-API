from rest_framework import viewsets, mixins,status
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from core.models import Tag, Ingredient, Recipe
from recipe import serializers
from rest_framework.decorators import action
from rest_framework.response import Response


class BaseRecipeAttrViewSet(viewsets.GenericViewSet,
                            mixins.ListModelMixin,
                            mixins.CreateModelMixin):
    """Base class for recipe attrebutes"""
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        """return objects for current authenticated user only"""
        return self.queryset.filter(user=self.request.user).order_by('-name')

    def perform_create(self,serializer):
        """create new attrebutes"""
        serializer.save(user=self.request.user)



class TagViewSet(BaseRecipeAttrViewSet):
    """manage tags in the database"""

    queryset = Tag.objects.all()
    serializer_class = serializers.TagSerializer


class IngredientViewSet(BaseRecipeAttrViewSet):
    """manage ingredients in the database"""

    serializer_class = serializers.IngredientSerializer
    queryset = Ingredient.objects.all()


class RecipeViewSet (viewsets.ModelViewSet):
    """manage recipes in the database"""

    serializer_class = serializers.RecipeSerializer
    queryset = Recipe.objects.all()
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        """retrive the recipes for authenticated user"""
        return self.queryset.filter(user=self.request.user)


    def get_serializer_class(self):
        """:return apporpriate serializer for request if we want recipe's list return RecipeSerializer
        else if we want retrieve return RecipeDetailSerializer"""
        if self.action == 'retrieve':
            return serializers.RecipeDetailSerializer
        if self.action == 'upload_image':
            return serializers.RecipeImageSrializer
        return self.serializer_class

    def perform_create(self, serializer):
        """Create a new recipe"""
        serializer.save(user=self.request.user)

    @action(methods=['POST'],detail=True,url_path='upload-image')
    def upload_image(self,request,pk=None):
        """upload image to a recipe"""
        recipe = self.get_object()
        serializer = self.get_serializer(
            recipe,
            request.data
        )

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data,status=status.HTTP_200_OK)

        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)