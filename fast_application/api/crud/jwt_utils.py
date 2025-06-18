import jwt

from core.config import settings

"""получаем токен"""
def encode_jwt(
        payload:dict,
        private_key:str = settings.auth_jwt.private_key_path.read_text(),
        algorithm:str = settings.auth_jwt.algorithm
        ):
    encode = jwt.encode(
        payload,
        private_key,
        algorithm
        )
    return encode

"""декодируем токен"""

def decode_jwt(token:str|bytes, public_key:str = settings.auth_jwt.public_key_path.read_text(), algorithm:str=settings.auth_jwt.algorithm):
    decode = jwt.decode(
        token,
        public_key,
        algorithms=[algorithm]
        )
    return decode