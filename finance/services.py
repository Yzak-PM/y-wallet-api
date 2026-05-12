from django.db.models import Sum
from accounts.models import Account
from transactions.models import Transaction

# ======= Accounts =======
def get_total_assets(user):
    result = Account.objects.filter(
        user=user,
        nature=Account.Nature.ASSET
    ).aggregate(total=Sum("balance"))

    return result["total"] or 0

def get_total_liabilities(user):
    result = Account.objects.filter(
        user=user,
        nature=Account.Nature.LIABILITY
    ).aggregate(total=Sum("balance"))

    return result["total"] or 0

def get_net_worth(user):
    assets = get_total_assets(user)
    liabilities = get_total_liabilities(user)
    return assets - liabilities

# ======= Transactions =======
def get_income_and_expense_by_date_range(user, start_date, end_date):
    transactions = Transaction.objects.filter(
        user=user,
        date__range=[start_date, end_date]
    )

    income = transactions.filter(type=Transaction.Type.INCOME).aggregate(
        total=Sum('amount')
    )['total'] or 0

    expense = transactions.filter(type=Transaction.Type.EXPENSE).aggregate(
        total=Sum('amount')
    )['total'] or 0

    return {
        'income': income,
        'expense': expense
    }

def get_expenses_by_category(user, start_date=None, end_date=None, category=None):
    transactions = Transaction.objects.filter(
        user=user,
        type=Transaction.Type.EXPENSE
    )

    if start_date and end_date:
        transactions = transactions.filter(
            date__range=[start_date, end_date]
        )

    if category:
        transactions = transactions.filter(
            category__id = category
        )

    result = (
        transactions
        .values('category__id', 'category__title', 'category__color')
        .annotate(total=Sum('amount'))
        .order_by('-total')
    )

    return [ # Retorna los resultados limpiados para el frontend
        {
            "category": item['category__title'], 
            "total": float(item['total']),
            "color": item['category__color']
        }
        for item in result
    ]