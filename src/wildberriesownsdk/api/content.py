from io import BufferedReader
from pathlib import Path
from typing import Dict

from wildberriesownsdk.api.base import WBAPIAction
from wildberriesownsdk.common import config


class ImageToArticleUploadAction(WBAPIAction):
    name = "Загрузить изображение к карточке товара"
    help_text = "Загружает изображение к выбранному артикулу на соответствующую позицию в карточке"

    path = "media/file"
    method = "POST"

    def __init__(
        self, api_connector, article: str, file: Path, image_number: int, page: int = 1
    ) -> None:
        super().__init__(api_connector, page=page)

        self.article = article
        self.image_number = image_number
        self.file = file
        self.files_data = self.read_file(self.file)

    def get_auth_headers(self):
        auth_headers = super().get_auth_headers()
        request_headers = {
            "X-Nm-Id": self.article,
            "X-Photo-Number": str(self.image_number),
        }
        return {
            **auth_headers,
            **request_headers,
        }

    def get_files(self):
        return self.files_data

    def get_url(self) -> str:
        return f"{config.BASE_CONTENT_API_URL}/{config.CONTENT_API_VERSION}/{self.path}"

    @staticmethod
    def read_file(file: Path) -> Dict[str, BufferedReader]:
        return {"uploadfile": open(file, "rb")}
