import json
import time
from datetime import datetime
from decimal import Decimal
from utils.aws.dynamodb import save_message, get_room_id, get_connection_ids
from utils.aws.websocket import send_message_to_connections
from functions.connect import connections  # 기존 connections 집합 불러오기
from utils.auth import get_current_user_info

async def send_message(event, context):
    # receiver_id = body['receiver_id']
    body = json.loads(event['body'])
    message = body.get('message', '')
    timestamp = body.get('timestamp', int(time.time() * 1000))
    message_id = timestamp
    
    token = body.get('token', None)  # 기본값 설정
    user_type = body.get('user_type', None)  # 기본값 설정
    receiver_id = body.get('receiver_id', None)  # 기본값 설정
    initial = body.get('initial', False)  # 기본값 설정

    user = get_current_user_info(token)
    user_type = user.get('user_type', user_type)
    if user_type == 'user':
        user_id = user['sub']
        seller_id = receiver_id
    elif user_type == 'seller':
        seller_id = user['sub']
        user_id = receiver_id
    room_id = get_room_id(user_id, seller_id)

    data = {
        'room_id': room_id,
        'user_type': user_type,
        'message': message,
        'user_id': user_id,
        'seller_id': seller_id,
        'initial': initial,
        'timestamp': timestamp,
    }
    # 메시지저장, 룸정보 업데이트
    room_info = save_message(data)


    # 같은 room_id에 있는 연결 필터링
    # connection_ids = [
    #     connection_id for connection_id, info in connections.items() if info['room_id'] == room_id
    # ]
    connection_ids = get_connection_ids(room_id)
    if isinstance(user_id, Decimal):
        user_id = str(user_id)
    if isinstance(seller_id, Decimal):
        seller_id = str(seller_id)
    if isinstance(timestamp, Decimal):
        timestamp_seconds = int(timestamp) / 1000
        timestamp = datetime.fromtimestamp(timestamp_seconds).strftime("%Y-%m-%d %H:%M:%S")
        
    
    if isinstance(room_info['last_message_at'], Decimal):
        timestamp_seconds = int(room_info['last_message_at']) / 1000
        room_info['last_message_at'] = datetime.fromtimestamp(timestamp_seconds).strftime("%Y-%m-%d %H:%M:%S")
    if isinstance(room_info['user_id'], Decimal):
        room_info['user_id'] = str(room_info['user_id'])
    if isinstance(room_info['seller_id'], Decimal):
        room_info['seller_id'] = str(room_info['seller_id'])
    if isinstance(room_info['user_unread_count'], Decimal):
        room_info['user_unread_count'] = str(room_info['user_unread_count'])
    if isinstance(room_info['seller_unread_count'], Decimal):
        room_info['seller_unread_count'] = str(room_info['seller_unread_count'])

    # 1. 최신 메시지 반환
    await send_message_to_connections(connection_ids, {
        'action': 'sendMessage',
        'sender_user_type': user_type,
        'user_id': user_id,
        'seller_id': seller_id,
        'message_id': message_id,
        'message': message,
        'timestamp': timestamp
    }, event)
    
    # 2. 룸정보 변경점 반환
    await send_message_to_connections(connection_ids, {
        'action': 'updateRoom',
        'sender_user_type': user_type,
        'room_info': room_info
    }, event)

    return {
        'action': 'sendMessage',
        'sender_user_type': user_type,
        'user_id': user_id,
        'seller_id': seller_id,
        'message_id': message_id,
        'message': message,
        'timestamp': timestamp
    }

