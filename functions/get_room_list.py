import json
from datetime import datetime
from decimal import Decimal
from utils.auth import get_current_user_info
from utils.aws.dynamodb import get_connection_ids, get_room_id, get_room_list as dynamodb_get_room_list, get_chat_history as fetch_chat_history
from utils.aws.websocket import send_message_to_connections


async def get_room_list(event, context):
    body = json.loads(event['body'])
    token = body.get('token', None)  # 기본값 설정
    user_type = body.get('user_type', None)  # 기본값 설정

    user = get_current_user_info(token)
    user_type = user.get('user_type', user_type)
    sender_id = user['sub']


    room_list = dynamodb_get_room_list(sender_id, user_type)
    room_id = None
    if user_type == 'user':
        user_id = sender_id
        seller_id = None
    elif user_type == 'seller':
        user_id = None
        seller_id = sender_id

    # 타임스탬프를 datetime으로 변환하여 출력하기
    
    for item in room_list:
        if isinstance(item['last_message_at'], Decimal):
            timestamp_seconds = int(item['last_message_at']) / 1000
            item['last_message_at'] = datetime.fromtimestamp(timestamp_seconds).strftime("%Y-%m-%d %H:%M:%S")
        if isinstance(item['user_id'], Decimal):
            item['user_id'] = str(item['user_id'])
        if isinstance(item['seller_id'], Decimal):
            item['seller_id'] = str(item['seller_id'])
        if isinstance(item['user_unread_count'], Decimal):
            item['user_unread_count'] = str(item['user_unread_count'])
        if isinstance(item['seller_unread_count'], Decimal):
            item['seller_unread_count'] = str(item['seller_unread_count'])

    connection_ids = get_connection_ids(room_id, user_id, seller_id)
    # 같은 room_id에 있는 연결 필터링
    # connection_ids = [
    #     connection_id for connection_id, info in connections.items() if info['room_id'] == room_id
    # ]
    await send_message_to_connections(connection_ids, {
        'action': 'getRoomList',
        'list': room_list,

    }, event)
    
    return {
        'statusCode': 200
    }
