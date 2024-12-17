from pathlib import Path

from wildberriesownsdk.api.base import WBAPIAction
from wildberriesownsdk.common import config


class ImageToArticleUploadAction(WBAPIAction):
    name = "Загрузить изображение к карточке товара"
    help_text = "Загружает изображение к выбранному артикулу на соответствующую позицию в карточке"

    path = "media/file"
    method = "POST"

    def __init__(
        self, api_connector, article: str, file: Path, image_number: int, page: int = 1
    ):
        super().__init__(api_connector, page=page)

        self.article = article
        self.image_number = image_number
        self.files_data = self._read_file(file)

    def _read_file(self, file: Path):
        with open(file, "rb") as f:
            files_data = {"uploadfile": (file, f)}

        return files_data

    def get_auth_headers(self) -> dict:
        request_headers = {
            "X-Nm-Id": self.article,
            "X-Photo-Number": str(self.image_number),
        }
        auth_headers = super().get_auth_headers()

        request_headers.update(auth_headers)
        return request_headers

    def get_files(self):
        return self.files_data

    def get_url(self) -> str:
        return f"{config.BASE_CONTENT_API_URL}/{config.CONTENT_API_VERSION}/{self.path}"