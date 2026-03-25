from rest_framework.routers import DefaultRouter
from .views import FinanceViewSet

router = DefaultRouter()
router.register('finance', FinanceViewSet, basename='finance')

urlpatterns = router.urls