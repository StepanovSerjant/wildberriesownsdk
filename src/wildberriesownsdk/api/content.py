from pathlib import Path

from wildberriesownsdk.api.base import WBAPIAction
from wildberriesownsdk.api.enums import WBScope


class ImageToArticleUploadAction(WBAPIAction):
    name = "Загрузить изображение к карточке товара"
    help_text = "Загружает изображение к выбранному артикулу на соответствующую позицию в карточке"

    method = "POST"
    path = "media/file"
    scope = WBScope.CONTENT.value

    def __init__(
        self, api_connector, article: str, file: Path, image_number: int, page: int = 1
    ):
        super().__init__(api_connector, page=page)

        self.article = article
        self.image_number = image_number
        self.file = file
        self.files_data = self.read_file(self.file)

    @property
    def own_auth_headers(self) -> dict:
        return {
            "X-Nm-Id": self.article,
            "X-Photo-Number": str(self.image_number),
        }

    def get_auth_headers(self) -> dict:
        auth_headers = super().get_auth_headers()
        auth_headers.update(**self.own_auth_headers)
        return auth_headers

    def get_files(self):
        return self.files_data

    @staticmethod
    def read_file(file: Path) -> dict:
        files_data = {"uploadfile": open(file, "rb")}
        return files_data
