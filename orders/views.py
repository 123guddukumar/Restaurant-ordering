from rest_framework import viewsets
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import MenuItem, Order, OrderItem, CompletedOrder, CompletedOrderItem
from .serializers import MenuItemSerializer, OrderSerializer, CompletedOrderSerializer
from django.db.models import Q
import logging

logger = logging.getLogger(__name__)

class MenuItemViewSet(viewsets.ModelViewSet):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer
    http_method_names = ['get', 'post', 'patch', 'put']

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            logger.info(f"Created menu item: {serializer.data['name']}, Available: {serializer.data['is_available']}")
            return Response(serializer.data, status=201)
        logger.error(f"Failed to create menu item: {serializer.errors}")
        return Response(serializer.errors, status=400)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        if serializer.is_valid():
            serializer.save()
            logger.info(f"Updated menu item {instance.id}: {serializer.data['name']}, Available: {serializer.data['is_available']}")
            return Response(serializer.data)
        logger.error(f"Failed to update menu item {instance.id}: {serializer.errors}")
        return Response(serializer.errors, status=400)

class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    http_method_names = ['get', 'post', 'patch']

    def get_queryset(self):
        status = self.request.query_params.get('status', 'open')
        return Order.objects.filter(status=status).distinct().order_by('-created_at')

    def create(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            order_data = serializer.create(serializer.validated_data)
            logger.info(f"Order created: ID {order_data['id']}, Customer ID: {order_data['customer_id']}, Items: {[item['id'] for item in order_data['items']]}")
            return Response(order_data, status=201)
        except Exception as e:
            logger.error(f"Error creating order: {str(e)}, Data: {request.data}")
            return Response({'status': 'error', 'message': str(e)}, status=500)

class CompletedOrderViewSet(viewsets.ModelViewSet):
    queryset = CompletedOrder.objects.all().order_by('-completed_at')
    serializer_class = CompletedOrderSerializer
    http_method_names = ['get']

@api_view(['PATCH'])
def update_order_item_status(request, order_item_id):
    try:
        order_item = OrderItem.objects.get(id=order_item_id)
        status = request.data.get('status')
        preparation_time = request.data.get('preparation_time')
        if status in ['confirmed', 'rejected']:
            order_item.status = status
            if status == 'confirmed' and preparation_time:
                order_item.preparation_time = int(preparation_time)
            else:
                order_item.preparation_time = None
            order_item.save()
            logger.info(f"Order item {order_item_id} updated to status: {status}, Preparation time: {order_item.preparation_time}")
            return Response({'status': 'success', 'message': f'Order item {status}'})
        logger.warning(f"Invalid status received for order item {order_item_id}: {status}")
        return Response({'status': 'error', 'message': 'Invalid status'}, status=400)
    except OrderItem.DoesNotExist:
        logger.error(f"Order item {order_item_id} not found")
        return Response({'status': 'error', 'message': 'Order item not found'}, status=404)
    except Exception as e:
        logger.error(f"Error in update_order_item_status: {str(e)}")
        return Response({'status': 'error', 'message': str(e)}, status=500)

@api_view(['PATCH'])
def complete_order(request, order_id):
    try:
        order = Order.objects.get(id=order_id)
        completed_order = CompletedOrder.objects.create(
            order_id=order.id,
            customer_id=order.customer.id,
            name=order.name,
            table_number=order.table_number,
            mobile_number=order.mobile_number,
            created_at=order.created_at
        )
        for item in order.items.all():
            CompletedOrderItem.objects.create(
                completed_order=completed_order,
                menu_item_name=item.menu_item.name,
                quantity=item.quantity,
                price=item.menu_item.price,
                status=item.status
            )
        order.status = 'completed'
        order.save()
        logger.info(f"Order {order_id} marked as completed, CompletedOrder ID: {completed_order.id}")
        return Response({'status': 'success', 'message': 'Order marked as completed'})
    except Order.DoesNotExist:
        logger.error(f"Order {order_id} not found")
        return Response({'status': 'error', 'message': 'Order not found'}, status=404)
    except Exception as e:
        logger.error(f"Error in complete_order: {str(e)}")
        return Response({'status': 'error', 'message': str(e)}, status=500)