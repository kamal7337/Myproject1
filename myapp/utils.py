from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

def send_websocket_notification(user, message):
    """
    Sends a real-time WebSocket notification to the user's WebSocket group.
    """
    channel_layer = get_channel_layer()
    group_name = f"user_{user.id}_notifications"  # Group name specific to the user

    # Send the notification to the WebSocket group
    async_to_sync(channel_layer.group_send)(
        group_name,
        {
            'type': 'send_notification',  # This is the method to call in the consumer
            'notification': message,  # Notification message to send
        }
    )
