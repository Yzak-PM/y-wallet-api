from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .serializers import CategorySerializer
from .models import Category

class CategoryViewSet(viewsets.ModelViewSet):
    """
    CRUD operations for Category model
    """
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user

        #* Superuser can see all categories
        if user.is_superuser:
            return Category.objects.all().order_by('title')
        
        #* Regular users can only see their own categories
        return Category.objects.filter(user=user).order_by('title')
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)