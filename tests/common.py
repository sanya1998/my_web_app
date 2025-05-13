from app.common.helpers.response import BaseResponse, ResponseType
from httpx import AsyncClient, Response
from starlette import status


def prepare_response(func):
    async def wrapper(
        *args, code: status = status.HTTP_200_OK, model: ResponseType | None = None, **kwargs
    ) -> ResponseType | Response:
        response = await func(*args, **kwargs)
        assert response.status_code == code
        if model:
            return BaseResponse[model].model_validate(response.json()).content
        return response

    return wrapper


class TestClient(AsyncClient):
    @prepare_response
    async def post(self, *args, **kwargs) -> ResponseType | Response:
        return await super().post(*args, **kwargs)

    @prepare_response
    async def get(self, *args, **kwargs) -> ResponseType | Response:
        return await super().get(*args, **kwargs)

    @prepare_response
    async def put(self, *args, **kwargs) -> ResponseType | Response:
        return await super().put(*args, **kwargs)

    @prepare_response
    async def patch(self, *args, **kwargs) -> ResponseType | Response:
        return await super().patch(*args, **kwargs)

    @prepare_response
    async def delete(self, *args, **kwargs) -> ResponseType | Response:
        return await super().delete(*args, **kwargs)
