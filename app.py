import json
import asyncio
from functions.connect import connect
from functions.disconnect import disconnect
from functions.send_message import send_message
from functions.get_chat_history import get_chat_history
from functions.get_room_list import get_room_list
from functions.change_room_status import change_room_status
from functions.set_translated_message import set_translated_message
from functions.translate_message import translate_message
from utils import return_result

def lambda_handler(event, context):
    # 비동기 핸들러를 동기적으로 실행
    return asyncio.run(async_lambda_handler(event, context))

async def async_lambda_handler(event, context):
    print('EVENT : ', event)
    print('CONTEXT : ', context)
    
    try:
        route_key = event['requestContext']['routeKey']
        
        if route_key == '$connect':
            await connect(event, context)
            return return_result.success()
        elif route_key == '$disconnect':
            await disconnect(event, context)
            return return_result.success()
        elif route_key == 'sendMessage':    
            #번역 플래그가 있으면 메시지 전송 후 번역처리    
            body = json.loads(event['body'])
            translate_and_save = body.get('translate_and_save', True)
            if translate_and_save:
                message_data = await send_message(event, context)
                await translate_message(event, context, message_data)
            else:
                await send_message(event, context)
            return return_result.success()
        elif route_key == 'getChatHistory':
            await get_chat_history(event, context)
            return return_result.success()
        elif route_key == 'getRoomList':
            await get_room_list(event, context)
            return return_result.success()
        elif route_key == 'changeRoomStatus':
            await change_room_status(event, context)
            return return_result.success()
        elif route_key == 'setTranslatedMessage':
            await set_translated_message(event, context)
            return return_result.success()
        else:
            print(f"Unknown routeKey: {route_key}")
            return return_result.bad_request(message="Unknown route key")
            
    except json.JSONDecodeError as e:
        print(f"JSON decode error: {e}")
        return return_result.bad_request(message="Invalid JSON format in request body")
    except KeyError as e:
        print(f"Missing key in event: {e}")
        return return_result.bad_request(message=f"Missing required key: {e}")
    except Exception as e:
        # Log the exception for debugging purposes
        print(f"An unexpected error occurred: {e}")
        # Potentially log the stack trace as well
        # import traceback
        # print(traceback.format_exc())
        
        # Return a generic server error response to the client
        return return_result.server_error(message="Internal server error")
