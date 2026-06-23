from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .serializers import TransactionSerializer, TransactionReadSerializer
from .models import Transaction

class TransactionViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user

        queryset = Transaction.objects.select_related(
            "account",
            "destination_account",
            "category"
        ).order_by("-date")

        if user.is_superuser:
            return queryset

        #Date range filter
        start_date = self.request.query_params.get("start_date")
        end_date = self.request.query_params.get("end_date")

        tx_type = self.request.query_params.get("type")          # income | expense | movement
        account = self.request.query_params.get("account")       # account id
        category = self.request.query_params.get("category")     # category id

        if start_date:
            queryset = queryset.filter(date__gte=start_date)
        if end_date:
            queryset = queryset.filter(date__lte=end_date)
        if tx_type:
            queryset = queryset.filter(type=tx_type)
        if account:
            queryset = queryset.filter(account_id=account)
        if category:
            queryset = queryset.filter(category_id=category)

        return queryset

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return TransactionReadSerializer
        return TransactionSerializer

    def _apply_transaction(self, transaction):
        account = transaction.account
        amount = transaction.amount

        # Movement
        if transaction.destination_account:
            dest = transaction.destination_account
            if dest.nature == "asset":
                dest.balance += amount
            else:
                dest.balance -= amount
            
            account.balance -= amount      # sale dinero del asset
            account.save()
            dest.save()
            return

        # Transacción simple según nature (gasto normal)
        if account.nature == "asset":
            if transaction.type == Transaction.Type.INCOME:
                account.balance += amount
            else:
                account.balance -= amount

        elif account.nature == "liability":
            account.balance += amount # aumenta la deuda

        account.save()

    def _revert_transaction(self, transaction):
        account = transaction.account
        amount = transaction.amount

        # Revertir pago de deuda
        if transaction.destination_account:
            dest = transaction.destination_account
            account.balance += amount
            dest.balance += amount
            account.save()
            dest.save()
            return

        # Revertir transacción simple (lógica inversa)
        if account.nature == "asset":
            if transaction.type == Transaction.Type.INCOME:
                account.balance -= amount
            else:
                account.balance += amount

        elif account.nature == "liability":
            if transaction.type == Transaction.Type.INCOME:
                account.balance += amount
            else:
                account.balance -= amount

        account.save()

    def perform_create(self, serializer):
        transaction = serializer.save(user=self.request.user)
        self._apply_transaction(transaction)

    def perform_update(self, serializer):
        old_transaction = self.get_object()
        self._revert_transaction(old_transaction)
        transaction = serializer.save()
        self._apply_transaction(transaction)

    def perform_destroy(self, instance):
        self._revert_transaction(instance)
        instance.delete()