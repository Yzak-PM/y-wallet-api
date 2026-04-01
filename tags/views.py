from rest_framework.response import Response
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from .serializers import TagSerializer
from .models import Tag
from .filters import TagFilter

class TagViewSet(viewsets.ModelViewSet):
    """
    CRUD operations for tag model
    """
    serializer_class = TagSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_class = TagFilter

    def get_queryset(self):
        user = self.request.user

        #* Superusers can see all tags, regular users can only see their own tags
        if user.is_superuser:
            return Tag.objects.all().order_by('name')
        return Tag.objects.filter(user=user).order_by('name')
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        # Limitar solo cuando hay búsqueda
        if request.query_params.get('search'):
            queryset = queryset[:10]
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)