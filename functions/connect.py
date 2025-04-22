# DynamoDB 임포트 주석 처리
import boto3
# DynamoDB 함수 임포트 주석 처리
from utils.aws.dynamodb import save_connection, get_room_id, reset_unread_count, testFunc
from utils.auth import get_current_user_info

# 메모리상에서 연결 정보를 관리하기 위한 딕셔너리로 변경
# 예: {connection_id: {'room_id': room_id, 'receiver_id': receiver_id}}
connections = {}  

async def connect(event, context):
    connection_id = event['requestContext']['connectionId']

    # 실제 서비스에서는 queryStringParameters에서 room_id와 token, user_type + 반대편 id(고객 or 판매자) 받아옴
    token = event['queryStringParameters']['token']
    user_type = event['queryStringParameters'].get('user_type')
    receiver_id = event['queryStringParameters'].get('receiver_id')
    user = get_current_user_info(token)
    # user_type = user.get('user_type', user_type)
    if user_type == 'user':
        user_id = user['sub']
        seller_id = receiver_id
    elif user_type == 'seller':
        seller_id = user['sub']
        user_id = receiver_id
    room_id = get_room_id(user_id, seller_id)
    # 기존 DynamoDB에 저장하던 부분을 주석 처리하고 메모리에 저장
    # testFunc()
    save_connection(connection_id, room_id, user_type, user_id, seller_id)
    # connections[connection_id] = {
    #     'connection_id': connection_id,
    #     'room_id': room_id,
    #     'receiver_id': receiver_id
    # }  # 메모리에 room_id와 receiver_id 포함하여 저장

    return {'statusCode': 200}
