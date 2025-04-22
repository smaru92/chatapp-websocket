
from jose import JWTError, jwt
from utils.setting import settings

secret_key = settings.ONDOCJP_SECRET_KEY
algorithm = settings.ONDOCJP_ALGORITHM

def get_current_user_info(token: str):
    payload = jwt.decode(token, secret_key, algorithms=[algorithm], options={"leeway": 10})

    if 'id' in payload:
        payload['sub'] = payload['id']
    if 'user_type' in payload:
        del payload['user_type']
    return payload