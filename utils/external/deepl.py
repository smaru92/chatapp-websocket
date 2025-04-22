# utils/deepl.py
from typing import List
from utils.setting import settings
import deepl

async def translate(message, source_lang, target_lang):
    # 번역 외부 API 요청 URL(DeepL)
#         url = "https://api-free.deepl.com/v2/translate"
#         headers = {
#             "Authorization": f"DeepL-Auth-Key 782360dc-b832-41fe-a145-bb4a716fbece:fx",  # Authorization 헤더 추가
#             "Content-Type": "application/json"
#         }
#
#         # 요청 보내기
#         async with httpx.AsyncClient() as client:
#             response = await client.post(url, json=request.dict())
#             response.raise_for_status()  # HTTP 에러가 있으면 예외 발생
#         # 응답 데이터 처리
#         data = response.json()
#         print(data)
    auth_key = settings.DEEPL_AUTH_KEY
    translator = deepl.Translator(auth_key)
    if target_lang == 'EN':
        target_lang = 'EN-US'
    if target_lang == 'ZH':
        target_lang = 'ZH-HANS'
    if target_lang == 'PT':
        target_lang = 'PT-BR'

    result = translator.translate_text(message, target_lang=target_lang)
    result = vars(result)
    result['request_text'] = message
    result['source_lang'] = source_lang
    result['target_lang'] = target_lang
    return result
    #print(result.text)  # "Bonjour, le monde !"
