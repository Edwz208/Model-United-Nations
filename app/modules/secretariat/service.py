# app/modules/secretariat/service.py

from app.modules.secretariat.repository import SecretariatRepository
from app.modules.secretariat.models import Secretariat
from app.modules.secretariat.schemas import SecretariatOut
from app.core.exceptions import SecretariatNotFoundException

class SecretariatService:
    def __init__(self, repository: SecretariatRepository) -> None:
        self.repository = repository

    async def get_all_execs(self) -> list[SecretariatOut]:
        members = await self.repository.list_all()
        return [SecretariatOut.model_validate(member) for member in members]

    async def post_exec(self, name: str, position: str) -> SecretariatOut:
        member = await self.repository.create(Secretariat(name=name, position=position))
        return SecretariatOut.model_validate(member)

    async def delete_exec(self, secretariat_id: int) -> SecretariatOut:
        member = await self.repository.get_by_id(secretariat_id)
        if not member:
            raise SecretariatNotFoundException(secretariat_id)
        out = SecretariatOut.model_validate(member)
        await self.repository.delete(member)
        return out

    async def update_exec(self, name: str | None, position: str | None, secretariat_id: int) -> SecretariatOut:
        member = await self.repository.get_by_id(secretariat_id)
        if not member:
            raise SecretariatNotFoundException(secretariat_id)
        if name is not None:
            member.name = name
        if position is not None:
            member.position = position
        updated = await self.repository.update(member)
        return SecretariatOut.model_validate(updated)
