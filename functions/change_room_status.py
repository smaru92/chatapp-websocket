import json
import time
from utils.aws.dynamodb import save_room_status, get_room_id, get_connection_ids
from utils.aws.websocket import send_message_to_connections
from functions.connect import connections  # 기존 connections 집합 불러오기
from utils.auth import get_current_user_info

async def change_room_status(event, context):
    # receiver_id = body['receiver_id']
    body = json.loads(event['body'])

    token = body.get('token', None)  # 기본값 설정
    user_type = body.get('user_type', None)  # 기본값 설정
    receiver_id = body.get('receiver_id', None)  # 기본값 설정
    room_status = body.get('room_status', None)

    user = get_current_user_info(token)
    user_type = user.get('user_type', user_type)
    if user_type == 'user':
        user_id = user['sub']
        seller_id = receiver_id
    elif user_type == 'seller':
        seller_id = user['sub']
        user_id = receiver_id
    room_id = get_room_id(user_id, seller_id)

    save_room_status(room_id, user_type, user_id, seller_id, room_status)

    connection_ids = get_connection_ids(room_id)
    # 같은 room_id에 있는 연결 필터링
    # connection_ids = [
    #     connection_id for connection_id, info in connections.items() if info['room_id'] == room_id
    # ]
    await send_message_to_connections(connection_ids, {
        'action': 'changeRoomStatus',
        'user_id': user_id,
        'seller_id': seller_id,
        'room_status': room_status
    }, event)

    return {
        'statusCode': 200
    }
