import boto3
from boto3.dynamodb.conditions import Key
from datetime import datetime
from botocore.exceptions import ClientError

dynamodb = boto3.resource('dynamodb')
connections_table = dynamodb.Table('chat-connection')
messages_table = dynamodb.Table('chat-message')
rooms_table = dynamodb.Table('chat-room')

def save_connection(connection_id, room_id, user_type, user_id=None, seller_id=None):
    if user_id:
        user_id=str(user_id)
    if seller_id:
        seller_id=str(seller_id)
    # 중복 항목 체크
    response = connections_table.scan(
        FilterExpression=Key('room_id').eq(room_id) & Key('user_id').eq(user_id) & Key('seller_id').eq(seller_id)
    )
    items = response.get('Items', [])

    # 기존 항목 삭제
    for item in items:
        if user_type == item['user_type']:
            # 각 항목의 Primary Key를 이용해 삭제
            connections_table.delete_item(
                Key={
                    'connection_id': item['connection_id']  # Primary Key로 실제 키 이름 변경
                }
            )

    connections_table.put_item(
        Item={
            'connection_id': connection_id,
            'user_id': user_id,
            'seller_id': seller_id,
            'room_id': room_id,
            'user_type': user_type
        }
    )

def delete_connection(connection_id):
    connections_table.delete_item(Key={'connection_id': connection_id})
"""
    data = {
        'room_id': 채팅방 ID
        'user_type': 작성한 유저타입
        'message': 메시지
        'user_id': 사용자 ID
        'seller': 판매자 ID
        'initial': // 알림여부, true면 관리자만 확인할 수 있음
        'timestamp': timestamp,
    }
"""
def save_message(data):    
    if 'user_id' in data:
        data['user_id']=str(data['user_id'])
    else:
        data['user_id']=None
    if 'seller_id' in data:
        data['seller_id']=str(data['seller_id'])
    else:
        data['seller_id']=None
    sender_id = ''
    has_unread = 'true'
    if data['user_type'] == 'user':
        sender_id = data['user_id']
        sender_user_id = data['user_id']
        sender_seller_id = None
        seller_unread_count = 1
        user_unread_count = 0
        update_expr = """
            SET seller_unread_count = if_not_exists(seller_unread_count, :start) + :inc,
                seller_has_unread = :has_unread,
                last_message = :message,
                last_message_at = :timestamp,
                last_message_sender_type = :user_type,
                last_message_sender_id = :sender_id
        """
    if data['user_type'] == 'seller':
        sender_id = data['seller_id']
        sender_user_id = None
        sender_seller_id = data['seller_id']
        seller_unread_count = 0
        user_unread_count = 1
        update_expr = """
            SET user_unread_count = if_not_exists(user_unread_count, :start) + :inc,
                user_has_unread = :has_unread,
                last_message = :message,
                last_message_at = :timestamp,
                last_message_sender_type = :user_type,
                last_message_sender_id = :sender_id
        """

    # 메시지 저장
    messages_table.put_item(
        Item={
            'room_id': data['room_id'],
            'timestamp': data['timestamp'],
            'user_type': data['user_type'],
            'user_id': sender_user_id,
            'seller_id': sender_seller_id,
            'message': data['message'],
            'initial':data['initial'],
            'message_type': 'text',
            'has_unread' : has_unread
        }
    )

    # Room 데이터 업데이트(최근 메시지, 읽지않은 메시지 수)
    message_data = {
        'room_id': data['room_id'],
        'user_id':data['user_id'],
        'seller_id':data['seller_id'],
        'user_type':data['user_type'],
        'sender_id':sender_id,
        'message':data['message'],
        'timestamp':data['timestamp'],
        'seller_unread_count':seller_unread_count,
        'user_unread_count':user_unread_count,
        'has_unread':has_unread,
        'update_expr':update_expr,
    }
    
    # 보낸 메시지에따른 방정보 수정
    # 변경된 룸 정보를 반환
    return upsert_room(data['user_id'], data['seller_id'], message_data)


def upsert_room(user_id, seller_id, message_data):
    if user_id:
        user_id=str(user_id)
    if seller_id:
        seller_id=str(seller_id)
    try:
        # 1. room_id로 데이터 조회
        response = rooms_table.get_item(Key={'room_id': message_data['room_id']})
        if 'Item' in response:
            # 기존 데이터 업데이트
            # 적절한 Partition Key와 Sort Key를 선택
            rooms_table.update_item(
                Key={
                    'room_id': message_data['room_id']
                },
                UpdateExpression=message_data['update_expr'],
                ExpressionAttributeValues={
                    ':start': 0,
                    ':inc': 1,
                    ':has_unread': message_data['has_unread'],
                    ':message': message_data['message'],
                    ':timestamp': message_data['timestamp'],
                    ':user_type': message_data['user_type'],
                    ':sender_id': message_data['sender_id'],
                },
                ReturnValues="UPDATED_NEW"
            )
            room_info = response['Item']
        else:
            # 데이터가 없으면 새 항목 추가
            rooms_table.put_item(
                Item={
                    'room_id': message_data['room_id'],
                    'user_id': user_id,
                    'seller_id': seller_id,
                    'user_unread_count': message_data['user_unread_count'],
                    'seller_unread_count': message_data['seller_unread_count'],
                    'user_has_unread': 'true',
                    'seller_has_unread': 'true',
                    'last_message': message_data['message'],
                    'last_message_at': message_data['timestamp'],
                    'last_message_sender_type': message_data['user_type'],
                    'last_message_sender_id': message_data['sender_id'],
                    'room_status': '상담중'
                }
            )
            
            room_info = {
                'room_id': message_data['room_id'],
                'user_id': user_id,
                'seller_id': seller_id,
                'user_unread_count': message_data['user_unread_count'],
                'seller_unread_count': message_data['seller_unread_count'],
                'last_message': message_data['message'],
                'last_message_at': message_data['timestamp'],
                'last_message_sender_type': message_data['user_type'],
                'last_message_sender_id': message_data['sender_id'],
                'room_status': '상담중'
            }
        return room_info
    except ClientError as e:
        print(f"An error occurred: {e.response['Error']['Message']}")


def get_connection_ids(room_id, user_id=None, seller_id=None):
    if user_id:
        user_id=str(user_id)
    if seller_id:
        seller_id=str(seller_id)
    if room_id is not None:
        if user_id is not None:
            keys = Key('room_id').eq(room_id) & Key('user_id').eq(user_id)
        elif seller_id is not None:
            keys = Key('room_id').eq(room_id) & Key('seller_id').eq(seller_id)
        else:
            keys = Key('room_id').eq(room_id)

        response = connections_table.scan(
            FilterExpression=keys
        )
    else:
        if user_id is not None:
            response = connections_table.query(
                IndexName='user_id-index',
                KeyConditionExpression=(
                    Key('user_id').eq(user_id)
                ),
                ScanIndexForward=True
            )
        elif seller_id is not None:
            response = connections_table.query(
                IndexName='seller_id-index',
                KeyConditionExpression=(
                    Key('seller_id').eq(seller_id)
                ),
                ScanIndexForward=True
            )
        else:
            keys = Key('room_id').eq(room_id)
            response = connections_table.scan(
                FilterExpression=keys
            )
            
    result = []
    for item in response['Items']: 
        if user_id is None and seller_id is None:
            result.append(item['connection_id'])            
        else:
            if user_id is not None:
                if item['user_type'] == 'user':
                    result.append(item['connection_id'])
            if seller_id is not None:
                if item['user_type'] == 'seller':
                    result.append(item['connection_id'])
    return result

def get_chat_history(room_id, start_time=None, end_time=None):
    if start_time and end_time:
        response = messages_table.query(
            KeyConditionExpression=(
                Key('room_id').eq(room_id) & Key('timestamp').between(start_time, end_time)
            ),
            ScanIndexForward=True
        )
    else:
        response = messages_table.query(
            KeyConditionExpression=Key('room_id').eq(room_id),
            ScanIndexForward=True
        )
    return response['Items']

def get_room_list(sender_id, user_type):
    if sender_id:
        sender_id=str(sender_id)
    if user_type == 'user':
        response = rooms_table.query(
            IndexName='user_id-index',
            KeyConditionExpression=(
                Key('user_id').eq(sender_id)
            ),
            ScanIndexForward=True
        )
    elif user_type == 'seller':
        response = rooms_table.query(
            IndexName='seller_id-index',
            KeyConditionExpression=(
                Key('seller_id').eq(sender_id)
            ),
            ScanIndexForward=True
        )
    return response['Items']

def save_room_status(room_id, user_type, user_id, seller_id, room_status):
    try:
        # 1. room_id로 데이터 조회
        response = rooms_table.get_item(Key={'room_id': room_id})
        
        update_expr = """
            SET room_status = :room_status
        """
        if 'Item' in response:
            # 기존 데이터 업데이트
            # 적절한 Partition Key와 Sort Key를 선택
            rooms_table.update_item(
                Key={
                    'room_id': room_id
                },
                UpdateExpression=update_expr,
                ExpressionAttributeValues={
                    ':room_status': room_status,
                },
                ReturnValues="UPDATED_NEW"
            )
            print("Item updated successfully!")
    except ClientError as e:
        print(f"An error occurred: {e.response['Error']['Message']}")

def save_translated_message(room_id, user_type, message, target_lang, user_id, seller_id, message_id):
    try:
        # 1. room_id로 데이터 조회
        expression_parameter = {}
        if user_type == 'seller':
            update_expr = """
                SET seller_translated_message = :translated_seller_message,
                    seller_target_lang = :seller_target_lang
            """
            expression_parameter[':translated_seller_message'] = message
            expression_parameter[':seller_target_lang'] = target_lang
        elif user_type == 'user':
            update_expr = """
                SET user_translated_message = :translated_user_message,
                    user_target_lang = :user_target_lang
            """
            expression_parameter[':translated_user_message'] = message
            expression_parameter[':user_target_lang'] = target_lang
            
        print(expression_parameter)
        # 기존 데이터 업데이트
        # 적절한 Partition Key와 Sort Key를 선택
        messages_table.update_item(
            Key={
                'room_id': room_id,
                'timestamp': int(message_id)
            },
            UpdateExpression=update_expr,
            ExpressionAttributeValues=expression_parameter,
            ReturnValues="UPDATED_NEW"
        )
        print("Item updated successfully!")
    except ClientError as e:
        print(f"An error occurred: {e.response['Error']['Message']}")

def get_room_id(user_id, seller_id):
    return f'{user_id}__room__{seller_id}'

def reset_unread_count(room_id, user_type):
    # 1. room_id로 데이터 조회
    response = rooms_table.get_item(Key={'room_id': room_id})
    print('ROOM RESPONSE : ', response)
    if 'Item' in response:
        if user_type == "user":
            update_expr = "SET user_unread_count = :zero, user_has_unread = :has_unread"
        elif user_type == "seller":
            update_expr = "SET seller_unread_count = :zero, seller_has_unread = :has_unread"
        else:
            raise ValueError("Invalid User Type")

        response = rooms_table.update_item(
            Key={
                'room_id': room_id
            },
            UpdateExpression=update_expr,
            ExpressionAttributeValues={
                ':zero': 0,
                ':has_unread': 'false',
            },
            ReturnValues="UPDATED_NEW"
        )
        return response['Attributes']


def testFunc():
    # 업데이트 조건 설정
    room_id_value = "29048__room__test1"
    response = messages_table.scan(
        FilterExpression="room_id = :room_id_value AND attribute_exists(seller_id)",
        ExpressionAttributeValues={":room_id_value": room_id_value}
    )

    items = response.get('Items', [])

    # Step 2: 조회된 항목 중 seller_id가 null이 아닌 경우 user_id를 null로 업데이트
    for item in items:
        if item.get('seller_id') is not None:
            messages_table.update_item(
                Key={
                    "room_id": item['room_id'],  # 실제 테이블의 파티션 키로 대체
                    "timestamp": item['timestamp']             # 실제 테이블의 정렬 키로 대체
                },
                UpdateExpression="SET user_id = :null_value",
                ExpressionAttributeValues={":null_value": None},
                ReturnValues="UPDATED_NEW"
            )