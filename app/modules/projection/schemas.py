# app/modules/projection/schemas.py

from pydantic import BaseModel, Field
from typing import Optional, Annotated

class Projection(BaseModel):
    active_screen: Optional[str] = None
    temporary_speaker_1: Annotated[Optional[int], Field(strict=True, ge=0)] = None
    temporary_speaker_2: Annotated[Optional[int], Field(strict=True, ge=0)] = None
    temporary_speaker_3: Annotated[Optional[int], Field(strict=True, ge=0)] = None
    paging_system: Optional[bool] = None
    message: Annotated[Optional[str], Field(max_length=600)] = None
    vote_to_open_resolution_number: Annotated[Optional[int], Field(strict=True, ge=0)] = None
    vote_pass_fail_or_cancel: Optional[str] = None
    clear_vote: Optional[bool] = None
