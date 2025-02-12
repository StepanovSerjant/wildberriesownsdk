import pytz

from wildberriesownsdk.api.enums import WBScope

API_DATABASE_TZ = pytz.UTC
API_DATABASE_DATETIME_FORMAT = "%Y-%m-%dT%H:%M:%SZ"

BASE_MARKETPLACE_API_URL = "https://marketplace-api.wildberries.ru/api"
BASE_CONTENT_API_URL = "https://content-api.wildberries.ru/content"

MARKETPLACE_API_VERSION = "v3"
CONTENT_API_VERSION = "v3"

API_SCOPE_DATA_MAP = {
    WBScope.MARKETPLACE.value: {
        "url": BASE_MARKETPLACE_API_URL,
        "api_version": MARKETPLACE_API_VERSION,
    },
    WBScope.CONTENT.value: {
        "url": BASE_CONTENT_API_URL,
        "api_version": CONTENT_API_VERSION,
    },
}
API_AVAILABLE_SCOPES = API_SCOPE_DATA_MAP.keys()
