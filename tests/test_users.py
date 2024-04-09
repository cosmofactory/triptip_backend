from http import HTTPStatus

from httpx import AsyncClient


async def test_smoke_not_coming(ac: AsyncClient):
    response = await ac.get("/about_project")
    assert response.status_code == HTTPStatus.OK
    assert "Error" not in response.json().keys()
