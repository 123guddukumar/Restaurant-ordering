from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import OrderItem, Order
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
import logging
from .serializers import OrderItemSerializer, OrderSerializer

logger = logging.getLogger(__name__)

@receiver(post_save, sender=OrderItem)
def order_item_saved(sender, instance, **kwargs):
    channel_layer = get_channel_layer()
    order_item_data = OrderItemSerializer(instance).data
    async_to_sync(channel_layer.group_send)(
        'orders',
        {
            'type': 'order_item_notification',
            'order_item': order_item_data
        }
    )
    logger.info(f"Sent order_item_notification for OrderItem {instance.id}, status: {instance.status}, order: {instance.order_id}")

@receiver(post_save, sender=Order)
def order_saved(sender, instance, **kwargs):
    channel_layer = get_channel_layer()
    order_data = OrderSerializer(instance).data
    async_to_sync(channel_layer.group_send)(
        'orders',
        {
            'type': 'order_notification',
            'order': order_data
        }
    )
    logger.info(f"Sent order_notification for Order {instance.id}")

@receiver(post_save, sender=Order)
def order_completed(sender, instance, **kwargs):
    if instance.status == 'completed':
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            'orders',
            {
                'type': 'order_completed_notification',
                'order_id': instance.id,
                'customer_id': str(instance.customer.id)
            }
        )
        logger.info(f"Sent order_completed_notification for Order {instance.id}, Customer ID: {instance.customer.id}")