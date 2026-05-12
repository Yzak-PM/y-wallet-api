from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from datetime import datetime
from finance.services import (
    get_total_assets,
    get_total_liabilities,
    get_net_worth,
    get_income_and_expense_by_date_range,
    get_expenses_by_category
)

class FinanceViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=["get"])
    def summary(self, request):
        user = request.user
        return Response({
            "assets": get_total_assets(user),
            "liabilities": get_total_liabilities(user),
            "net_worth": get_net_worth(user)
        })

    @action(detail=False, methods=["get"])
    def income_vs_expense(self, request):
        start_date, end_date, error = self._parse_date_range(request)
        if error:
            return Response({"detail": error}, status=status.HTTP_400_BAD_REQUEST)

        data = get_income_and_expense_by_date_range(
            request.user,
            start_date,
            end_date
        )
        return Response(data)

    @action(detail=False, methods=["get"])
    def expenses_by_category(self, request):
        start_date, end_date, category, error = self._parse_date_range(request, required=False)
        if error:
            return Response({"detail": error}, status=status.HTTP_400_BAD_REQUEST)

        data = get_expenses_by_category(request.user, start_date, end_date, category)
        return Response(data)

    def _parse_date_range(self, request, required=True):
        start_str = request.query_params.get("start_date")
        end_str = request.query_params.get("end_date")
        category = request.query_params.get("category") or None

        if required and not (start_str and end_str):
            return None, None, None, "start_date y end_date son requeridos."

        try:
            start_date = datetime.strptime(start_str, "%Y-%m-%d").date() if start_str else None
            end_date = datetime.strptime(end_str, "%Y-%m-%d").date() if end_str else None
        except ValueError:
            return None, None, None, "Formato de fecha inválido. Usa YYYY-MM-DD."

        return start_date, end_date, category, None