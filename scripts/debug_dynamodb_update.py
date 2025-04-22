import boto3
from boto3.dynamodb.conditions import Key

# DynamoDB 테이블 설정
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('chat-message')

# 업데이트 조건 설정
room_id_value = "29048__room__test1"

response = table.update_item(
    Key={
        "room_id": room_id_value  # 기본 키로 설정된 room_id를 지정
    },
    UpdateExpression="SET user_id = :null_value",  # user_id를 null로 설정
    ConditionExpression="attribute_exists(seller_id) AND seller_id <> :null_value",
    ExpressionAttributeValues={
        ":null_value": None  # None을 사용하여 null 값을 나타냄
    },
    ReturnValues="UPDATED_NEW"
)

print("Update Response:", response)
