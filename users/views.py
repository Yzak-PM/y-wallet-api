from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .serializers import UserSerializer
from .models import User

class UserViewSet(viewsets.ModelViewSet):
    """
    CRUD operations for User model
    """
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user

        #* Superusers can see all users
        if user.is_superuser:
            return User.objects.all()

        #* Normal users can only see themselves
        return User.objects.filter(id=user.id)

    @action(["POST"], detail=True, url_path='set-active')
    def set_active(self, request, pk):
        """
        Custom action to activate a user
        """
        user = self.get_object()
        user.is_active = True
        user.save()
        
        return Response({"status": "User Activated"})
    
    @action(["POST"], detail=True, url_path='set-inactive')
    def set_inactive(self, request, pk):
        """
        Custom action to deactivate a user
        """
        user = self.get_object()
        user.is_active = False
        user.save()

        return Response({"status": "User Inactivated"})