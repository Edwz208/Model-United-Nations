import pytest
from authentication import hash, verify, decode, generateJwt, get_current_user
from fastapi import HTTPException

@pytest.mark.asyncio
async def test_hash_and_verify():
    password = "mypassword123"
    hashed = await hash(password)
    assert hashed != password
    assert await verify(password, hashed) is True
    assert await verify("wrongpass", hashed) is False

@pytest.mark.asyncio
async def test_decode_valid():
    token = generateJwt({"id": 55}, "TEST_SECRET", 1)
    decoded = await decode(token, "TEST_SECRET")

    assert decoded["id"] == 55

@pytest.mark.asyncio
async def test_decode_invalid():
    with pytest.raises(Exception):
        await decode("BAD_TOKEN", "TEST_SECRET")

@pytest.mark.asyncio
async def test_get_current_user_valid():
    token = generateJwt({"id": 99, "role": "member"}, "TEST_SECRET", 1)
    user = await get_current_user(token)
    assert user['id'] == 99
    assert user['role'] == "member"

@pytest.mark.asyncio
async def test_get_current_user_bad_token():
    with pytest.raises(HTTPException):
        await get_current_user("INVALID")
