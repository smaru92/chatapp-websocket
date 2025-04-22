import json
from datetime import datetime
from decimal import Decimal
from utils.auth import get_current_user_info
from utils.aws.dynamodb import get_connection_ids, get_room_id, get_chat_history as fetch_chat_history, reset_unread_count
from utils.aws.websocket import send_message_to_connections


async def get_chat_history(event, context):
    body = json.loads(event['body'])
    token = body.get('token', None)  # 기본값 설정
    user_type = body.get('user_type', None)  # 기본값 설정
    receiver_id = body.get('receiver_id', None)  # 기본값 설정

    user = get_current_user_info(token)
    user_type = user.get('user_type', user_type)
    if user_type == 'user':
        user_id = user['sub']
        seller_id = receiver_id
    elif user_type == 'seller':
        seller_id = user['sub']
        user_id = receiver_id
    start_time = body.get('start_time', None)
    end_time = body.get('end_time', None)
    room_id = get_room_id(user_id, seller_id)
    if user_type == 'user':
        seller_id = None
    elif user_type == 'seller':
        user_id = None


    chat_history = fetch_chat_history(room_id, start_time, end_time)

    # 타임스탬프를 datetime으로 변환하여 출력하기
    for item in chat_history:
        item['message_id'] = item['timestamp']
        if isinstance(item['message_id'], Decimal):
            item['message_id']  = int(item['message_id'])
        if isinstance(item['timestamp'], Decimal):
            timestamp_seconds = int(item['timestamp']) / 1000
            item['timestamp'] = datetime.fromtimestamp(timestamp_seconds).strftime("%Y-%m-%d %H:%M:%S")
        if 'user_id' in item and isinstance(item['user_id'], Decimal):
            item['user_id'] = str(item['user_id'])
        if 'seller_id' in item and isinstance(item['seller_id'], Decimal):
            item['seller_id'] = str(item['seller_id'])

    
    # 접속한 유저 타입 안읽은 메시지 0으로 초기화
    reset_unread_count(room_id, user_type)
    connection_ids = get_connection_ids(room_id, user_id, seller_id)
    # 같은 room_id에 있는 연결 필터링
    # connection_ids = [
    #     connection_id for connection_id, info in connections.items() if info['room_id'] == room_id
    # ]
    await send_message_to_connections(connection_ids, {
        'action': 'getChatHistory',
        'history': chat_history,

    }, event)
    
    return {
        'statusCode': 200
    }
