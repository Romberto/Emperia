import httpx
from fastapi import APIRouter
from fastapi.params import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from api.crud.jwt_utils import _get_current_payload
from api.crud.user_utils import _get_current_user
from core.config import settings
from models.db_helper import db_helper
from models.user import UserBase
from shcemes.auth_sheams import SosRequest

router = APIRouter(
    tags=['Sendler'], prefix='/send', )

BOT_TOKEN = settings.bot_token
CHAT_ID = settings.chat_id


@router.post('/sos')
async def send_sos(data: SosRequest, payload: dict = Depends(_get_current_payload),
                   session: AsyncSession = Depends(db_helper.session_getter)):
    user: UserBase = await _get_current_user(session=session, payload=payload)
    if user:
        return {"user":user}
    else:
        return {"message": "not user"}
    # situation_text = {
    #     "dtp": "🚗 ДТП", "conflict": "⚠️ Конфликтная ситуация",
    #     }.get(data.type, "❓ Неизвестная ситуация")
    #
    # text = (f"<b>SOS сигнал!</b>\n"
    #         f"📝 Ситуация: {situation_text}\n"
    #         f"🌍 Координаты: "
    #         f"<a href='https://maps.google.com/?q={data.latitude},{data.longitude}'>Открыть карту</a>\n")
    #
    # if user.username:
    #     text = f"👤 @{user.username}\n" + text
    #
    # async with httpx.AsyncClient() as client:
    #     response = await client.post(
    #         f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage", json={
    #             "chat_id": CHAT_ID, "text": text, "parse_mode": "HTML", "disable_web_page_preview": True,
    #             }, )
    #
    # if response.status_code != 200:
    #     return {"message": "Ошибка отправки", "error": response.text}
    #
    # return {"message": "Сообщение отправлено"}