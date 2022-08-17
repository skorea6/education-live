from typing import Optional


class StatusCode:
    HTTP_200 = 200


class APISuccess:
    status_code: int
    data_count: int
    data: Optional[list]
    extra: Optional[list]

    def __init__(
        self,
        *,
        status_code: int = StatusCode.HTTP_200,
        data_count: int = 0,
        data: Optional[list] = None,
        extra: Optional[list] = None
    ):
        self.status_code = status_code
        self.data_count = data_count
        self.data = data
        self.extra = extra
        super().__init__()


class SuccessfulList(APISuccess):
    def __init__(self, data_count: int = 0, data: Optional[list] = None, extra: Optional[list] = None):
        super().__init__(
            status_code=StatusCode.HTTP_200,
            data_count=data_count,
            data=data,
            extra=extra
        )
