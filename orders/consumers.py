from channels.generic.websocket import AsyncJsonWebsocketConsumer
import logging

logger = logging.getLogger(__name__)

class OrderConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        await self.channel_layer.group_add("orders", self.channel_name)
        await self.accept()
        logger.info(f"WebSocket connected: {self.channel_name}")

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard("orders", self.channel_name)
        logger.info(f"WebSocket disconnected: {self.channel_name}")

    async def order_notification(self, event):
        await self.send_json({
            "type": "order_notification",
            "order": event["order"]
        })
        logger.info(f"Sent order_notification to {self.channel_name}")

    async def order_item_notification(self, event):
        await self.send_json({
            "type": "order_item_notification",
            "order_item": event["order_item"]
        })
        logger.info(f"Sent order_item_notification to {self.channel_name}, OrderItem: {event['order_item']['id']}")