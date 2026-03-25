from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .serializers import TagSerializer
from .models import Tag

class TagViewSet(viewsets.ModelViewSet):
    """
    CRUD operations for tag model
    """
    serializer_class = TagSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user

        #* Superuser can see all tags
        if user.is_superuser:
            return Tag.objects.all().order_by('name')
        
        #* Regular users can only see their own tags
        return Tag.objects.filter(user=user).order_by('name')
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)