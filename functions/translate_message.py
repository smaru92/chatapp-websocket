
import json
import time
from datetime import datetime
from decimal import Decimal
from utils.auth import get_current_user_info
from utils.aws.dynamodb import save_message, get_room_id, get_connection_ids, save_translated_message
from utils.aws.websocket import send_message_to_connections
from utils.external import deepl
from functions.connect import connections  # 기존 connections 집합 불러오기

async def translate_message(event, context, message_data):
    # receiver_id = body['receiver_id']
    body = json.loads(event['body'])
    message = body.get('message', '')
    if 'message_id' in message_data and message_data['message_id'] is not None:
        message_id = message_data['message_id']
    else:
        message_id = body.get('message_id')
        
    if 'timestamp' in message_data and message_data['timestamp'] is not None:
        timestamp = message_data['timestamp']
    else:
        timestamp = body.get('timestamp')
    
    token = body.get('token', None)  # 기본값 설정
    user_type = body.get('user_type', None)  # 기본값 설정
    receiver_id = body.get('receiver_id', None)  # 기본값 설정
    
    target_lang = body.get('target_lang', 'JA')  # 기본값 설정
    source_lang = body.get('source_lang', 'JA')  # 기본값 설정
    
    try:
        user = get_current_user_info(token)
        user_type = user.get('user_type', user_type)
        if user_type == 'user':
            user_id = user['sub']
            seller_id = receiver_id
        elif user_type == 'seller':
            seller_id = user['sub']
            user_id = receiver_id
        room_id = get_room_id(user_id, seller_id)

        translated_message = await deepl.translate(
            message=message,
            source_lang=source_lang,
            target_lang=target_lang
        )
        # 번역 메시지 정보 업데이트
        save_translated_message(
            room_id=room_id,
            user_type=user_type,
            message=translated_message['text'],
            target_lang=target_lang,
            user_id=user_id,
            seller_id=seller_id,
            message_id=message_id
        )


        # 같은 room_id에 있는 연결 필터링
        # connection_ids = [
        #     connection_id for connection_id, info in connections.items() if info['room_id'] == room_id
        # ]
        
        # 메시지를 받는 상대방에게 번역메시지 전송
        if user_type == 'user':
            # sender_user_id = user['sub']
            sender_seller_id = receiver_id
        elif user_type == 'seller':
            # sender_seller_id = user['sub']
            sender_user_id = receiver_id
            
        connection_ids = get_connection_ids(room_id=room_id)
        if isinstance(user_id, Decimal):
            user_id = str(user_id)
        if isinstance(seller_id, Decimal):
            seller_id = str(seller_id)
        if isinstance(timestamp, Decimal):
            timestamp_seconds = int(timestamp) / 1000
            timestamp = datetime.fromtimestamp(timestamp_seconds).strftime("%Y-%m-%d %H:%M:%S")
        
    # 1. 요청 메시지 데이터 반환
        # 메시지 전송
        send_data = {
            'action': 'setTranslatedMessage',
            'sender_user_type': user_type,
            'user_id': user_id,
            'seller_id': seller_id,
            'message_id': message_id,
            'target_lang': target_lang,
            'translated_message': translated_message['text'],
            'timestamp': timestamp
        }
        print('send_data')
        print(send_data)
        print('connection_ids')
        print(connection_ids)
        await send_message_to_connections(connection_ids, send_data, event)
    except Exception as e:
        print(f"WebSocket Send Error: {e}")  # 에러 로그 출력

    return {
        'statusCode': 200
    }
