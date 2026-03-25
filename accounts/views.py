from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated, AllowAny
from .serializers import AccountSerializer
from .models import Account

class AccountViewSet(viewsets.ModelViewSet):
    """
    CRUD operations for Account model
    """
    serializer_class = AccountSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user

        #* Superusers can see all accounts
        if user.is_superuser:
            return Account.objects.all()
        
        #* Normal users can only see their own accounts
        return Account.objects.filter(user=user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
        
