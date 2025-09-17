from rest_framework import serializers
from .models import MenuItem, Order, OrderItem, Customer, CompletedOrder, CompletedOrderItem
import logging

logger = logging.getLogger(__name__)

class MenuItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = MenuItem
        fields = ['id', 'name', 'price', 'image', 'is_available']

class OrderItemSerializer(serializers.ModelSerializer):
    menu_item = MenuItemSerializer(read_only=True)
    menu_item_id = serializers.PrimaryKeyRelatedField(
        queryset=MenuItem.objects.all(), source='menu_item', write_only=True
    )
    order = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = OrderItem
        fields = ['id', 'menu_item', 'menu_item_id', 'quantity', 'status', 'preparation_time', 'order']

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        logger.info(f"Serializing OrderItem {instance.id}, data: {ret}")
        return ret

class CompletedOrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = CompletedOrderItem
        fields = ['id', 'menu_item_name', 'quantity', 'price', 'status']

class CompletedOrderSerializer(serializers.ModelSerializer):
    items = CompletedOrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = CompletedOrder
        fields = ['order_id', 'customer_id', 'name', 'table_number', 'mobile_number', 'created_at', 'completed_at', 'items']

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True)
    customer_id = serializers.UUIDField(read_only=True, source='customer.id')
    customer_id_write = serializers.UUIDField(write_only=True, source='customer_id')

    class Meta:
        model = Order
        fields = ['id', 'name', 'table_number', 'mobile_number', 'items', 'created_at', 'customer_id', 'customer_id_write', 'status']

    def create(self, validated_data):
        items_data = validated_data.pop('items')
        customer_id = validated_data.pop('customer_id')
        try:
            customer, created = Customer.objects.get_or_create(id=customer_id)
            logger.info(f"Customer {'created' if created else 'retrieved'}: {customer.id}")
            order = Order.objects.filter(customer=customer, status='open').first()
            if not order:
                order = Order.objects.create(customer=customer, **validated_data)
                logger.info(f"Created new order: ID {order.id}, Customer ID: {customer.id}")
            else:
                for field, value in validated_data.items():
                    setattr(order, field, value)
                order.save()
                logger.info(f"Updated existing order: ID {order.id}, Customer ID: {customer.id}")
            for item_data in items_data:
                existing_item = OrderItem.objects.filter(
                    order=order,
                    menu_item=item_data['menu_item'],
                    status='pending'
                ).first()
                if existing_item:
                    existing_item.quantity += item_data['quantity']
                    existing_item.save()
                    logger.info(f"Updated OrderItem {existing_item.id}, Quantity: {existing_item.quantity}")
                else:
                    new_item = OrderItem.objects.create(order=order, **item_data)
                    logger.info(f"Created OrderItem {new_item.id}, MenuItem: {new_item.menu_item_id}")
            order.refresh_from_db()
            order_serializer = OrderSerializer(order)
            logger.info(f"Order created/updated: ID {order.id}, Customer ID: {customer.id}, Items: {[item.id for item in order.items.all()]}")
            return order_serializer.data
        except Exception as e:
            logger.error(f"Error creating order: {str(e)}")
            raise

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        logger.info(f"Serializing Order {instance.id}, data: {ret}")
        return ret