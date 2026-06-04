class WBAPIException(Exception):
    pass


class WBAPIBadRequestException(Exception):
    pass


class WBAPIUnauthorizedException(Exception):
    pass


class WBAPIForbiddenException(Exception):
    pass


class WBAPINotFoundException(Exception):
    pass


class WBAPIThrottlingException(Exception):
    pass
