from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import MenuItemViewSet, OrderViewSet, CompletedOrderViewSet, update_order_item_status, complete_order

router = DefaultRouter()
router.register(r'menu', MenuItemViewSet)
router.register(r'orders', OrderViewSet)
router.register(r'completed-orders', CompletedOrderViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('order-items/<int:order_item_id>/status/', update_order_item_status, name='update-order-item-status'),
    path('orders/<int:order_id>/complete/', complete_order, name='complete-order'),
]