from typing import Optional


class StatusCode:
    HTTP_200 = 200


class APISuccess:
    status_code: int
    paging: Optional[list]
    data: Optional[list]

    def __init__(
        self,
        *,
        status_code: int = StatusCode.HTTP_200,
        paging: Optional[list] = None,
        data: Optional[list] = None
    ):
        self.status_code = status_code
        self.paging = paging
        self.data = data
        super().__init__()


class PagingSuccessful(APISuccess):
    def __init__(self, paging: Optional[list] = None, data: Optional[list] = None):
        super().__init__(
            status_code=StatusCode.HTTP_200,
            paging=paging,
            data=data
        )