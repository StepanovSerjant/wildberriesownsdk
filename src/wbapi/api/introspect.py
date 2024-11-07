import datetime
from dataclasses import dataclass
from typing import List

from wbapi.api.base import WBAPIAction
from wbapi.common import config
from wbapi.common.exceptions import APIKeyIntrospectionException


@dataclass(frozen=True)
class WBIntrospectAPIKeySummary:
    deleted: bool
    is_sandbox: bool
    expired: bool
    scopes_decoded: List[str]
    expires_at: str

    def __post_init__(self):
        self.validate()

    def validate(self):
        if self.deleted:
            validation_error_text = "Ваш API токен удалён."
        elif self.is_sandbox:
            validation_error_text = "Ваш API токен предназначен только для песочницы."
        elif self.expired:
            validation_error_text = "Действие вашего API токена прекращено, необходимо создать новый в личном кабинете WB."
        elif expiration_minutes_left := self.expiration_minutes_left:
            validation_error_text = f"Действие вашего API токена прекратится через {expiration_minutes_left} минут, необходимо создать новый в личном кабинете WB."
        else:
            validation_error_text = None

        if validation_error_text:
            validation_error_text += "\nБолее подробная информация об API токене https://openapi.wildberries.ru/general/authorization/ru/"
            raise APIKeyIntrospectionException(validation_error_text)


    @property
    def expired_at_dtm(self) -> datetime.datetime:
        return (
            datetime.datetime
            .strptime(self.expires_at, config.API_DATABASE_DATETIME_FORMAT)
            .replace(tzinfo=config.API_DATABASE_TZ)
        )

    @property
    def expiration_summary(self) -> str:
        expired_at_str = self.expired_at_dtm.strftime("%Y-%m-%d %H:%M")
        return f"Срок API токена истекает {expired_at_str}."

    @property
    def expiration_minutes_left(self) -> int:
       return int((self.expired_at_dtm - datetime.datetime.now(tz=config.API_DATABASE_TZ)).total_seconds() // 60)


class IntrospectAPIKeyAPIAction(WBAPIAction):
    name = "Получить информацию об АПИ ключе"
    help_text = (
        "Эндпоинт со страницы https://openapi.wildberries.ru/jwt/ru/."
        "Возвращает полноценную информацию о токене."
    )

    method = "GET"

    def get_auth_headers(self) -> dict:
        return {"x-introspect": self.api_key, "accept": "application/json"}

    def get_url(self) -> str:
        return "https://common-api.wildberries.ru/open-utils/tokens/introspect-v2"
