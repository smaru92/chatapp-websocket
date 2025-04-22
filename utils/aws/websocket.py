import boto3
import json
import websockets

async def send_message_to_connections(connection_ids, message, event):

    # 로컬환경에서는 aws boto3이 실행안되기때문에 로컬용 코드사용
    # async with websockets.connect("ws://localhost:8765") as websocket:
    #     for connection_id in connection_ids:
    #         await websocket.send(json.dumps({"connection_id": connection_id, "message": message}))
    #         print(f"Sent message to {connection_id}")

    # aws boto3
    apigw_management = boto3.client(
        'apigatewaymanagementapi',
        endpoint_url=f"https://{event['requestContext']['domainName']}/{event['requestContext']['stage']}"
    )

    for connection_id in connection_ids:
        try:
            apigw_management.post_to_connection(
                ConnectionId=connection_id,
                Data=json.dumps(message)
            )
        except Exception as e:
            print(f"Failed to send message to connection {connection_id}: {e}")
    return {
        'stateCode':200
    }
