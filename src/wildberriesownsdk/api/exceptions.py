class WBAPIException(Exception):
    pass


class WBAPIBadRequestException(WBAPIException):
    pass


class WBAPIUnauthorizedException(WBAPIException):
    pass


class WBAPIForbiddenException(WBAPIException):
    pass


class WBAPINotFoundException(WBAPIException):
    pass


class WBAPIThrottlingException(WBAPIException):
    pass
