from dataclasses import dataclass
from datetime import date, datetime
import traceback
from fastapi import Query
from fastapi.responses import Response, JSONResponse
import requests

from env import MicroEnv

@dataclass
class UserInfoDetail:
    id: int
    nickname: str
    email: str
    status: str
    picture: str
    social_id: str
    social_type: str
    created_at: str

@dataclass
class UserInfo:
    id: int
    nickname: str
    picture: str

@dataclass
class TokenPayload:
    id: int

@dataclass
class VerifyBody:
    success: bool
    payload: TokenPayload | str | Response

async def auth_method(token: str = Query(...)) -> VerifyBody:
    def error(code, msg):
        return VerifyBody(success=False, payload=JSONResponse(status_code=code, content={'error': msg} if msg else None))

    if not token.strip():
        return error(400, 'Invalid token')
    
    try:
        res = Auth.verify(token)

        if not res.success:
            return error(401, res.payload)
        
        res.payload = TokenPayload(**res.payload)  # type: ignore

        return res
    except KeyError: return VerifyBody(success=False, payload=Response(status_code=401))
    except: 
        traceback.print_exc()
        return error(500, 'micro service error')


class Auth:
    @staticmethod
    def verify(token: str, check_active: bool=True) -> VerifyBody:
        res = requests.get(
            f'http://{MicroEnv.AUTH}/internal/auth/verify',
            params={
                'token': token,
                'check_active': check_active
            }
        )

        if res.status_code != 200:
            raise Exception(res.status_code)
        
        return VerifyBody(**res.json())

    @staticmethod
    def user_info(userId: str) -> UserInfo | None:
        res = requests.get(
            f'http://{MicroEnv.AUTH}/internal/info/{userId}',
        )

        if res.status_code == 404:
            return None

        if res.status_code != 200:
            raise Exception(res.status_code)
        
        return UserInfo(**res.json()['profile'])
        
    @staticmethod
    def user_info_detail(userId: str) -> UserInfoDetail | None:
        res = requests.get(
            f'http://{MicroEnv.AUTH}/internal/info/{userId}/detail',
        )

        if res.status_code == 404:
            return None
            
        if res.status_code != 200:
            raise Exception(res.status_code)
        
        return UserInfoDetail(**res.json()['profile'])