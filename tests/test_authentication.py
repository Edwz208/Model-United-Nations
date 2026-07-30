# tests/test_authentication.py

import pytest
from app.core.security import hash, verify, decode, generate_access_token
from app.core.dependencies import get_current_user
from app.core.exceptions import AuthorizationException
from app.core.settings import get_settings

settings = get_settings()

@pytest.mark.asyncio
async def test_hash_and_verify():
    password = "mypassword123"
    hashed = await hash(password)
    assert hashed != password
    assert await verify(password, hashed) is True
    assert await verify("wrongpass", hashed) is False

@pytest.mark.asyncio
async def test_decode_valid():
    token = generate_access_token({"id": 55}, settings.SECRET_KEY, 1)
    decoded = await decode(token, settings.SECRET_KEY)

    assert decoded["id"] == 55

@pytest.mark.asyncio
async def test_decode_invalid():
    with pytest.raises(AuthorizationException):
        await decode("BAD_TOKEN", settings.SECRET_KEY)

@pytest.mark.asyncio
async def test_get_current_user_valid():
    token = generate_access_token({"id": 99, "role": "member"}, settings.SECRET_KEY, 1)
    user = await get_current_user(token)
    assert user['id'] == 99
    assert user['role'] == "member"

@pytest.mark.asyncio
async def test_get_current_user_bad_token():
    with pytest.raises(AuthorizationException):
        await get_current_user("INVALID")
