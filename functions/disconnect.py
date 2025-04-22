import boto3  # DynamoDB 임포트 주석 처리
from utils.aws.dynamodb import delete_connection  # DynamoDB 함수 임포트 주석 처리
from functions.connect import connections  # 기존 connections 집합 불러오기

async def disconnect(event, context):
    connection_id = event['requestContext']['connectionId']
    
    # 기존 DynamoDB에서 삭제하던 부분을 주석 처리하고 메모리에서 제거
    delete_connection(connection_id)
    # connections.discard(connection_id)  # 메모리에서 connection_id 삭제
    
    return {'statusCode': 200}
