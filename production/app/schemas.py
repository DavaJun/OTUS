import re
from datetime import date, datetime, timezone
from typing import Annotated, Literal
from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field, SecretStr, StringConstraints, field_validator
ShortText = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=100)]
Biography = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=2000)]
Gender = Literal['male', 'female', 'other', 'unspecified']
Password = Annotated[SecretStr, Field(min_length=8, max_length=128)]


class ProfileFields(BaseModel):
    first_name: ShortText
    second_name: ShortText
    birthdate: date
    gender: Gender
    biography: Biography
    city: ShortText


class RegisterRequest(ProfileFields):
    model_config = ConfigDict(extra='forbid')
    password: Password

    @field_validator('birthdate', mode='before')
    @classmethod
    def iso_date(cls, value):
        if not isinstance(value, str) or not re.fullmatch(r'[0-9]{4}-[0-9]{2}-[0-9]{2}', value):
            raise ValueError('Expected YYYY-MM-DD')
        return value

    @field_validator('birthdate')
    @classmethod
    def not_in_future(cls, value: date) -> date:
        if value > datetime.now(timezone.utc).date():
            raise ValueError('Birthdate cannot be in the future')
        return value

    @field_validator('first_name', 'second_name', 'biography', 'city')
    @classmethod
    def no_null_bytes(cls, value: str) -> str:
        if '\x00' in value:
            raise ValueError('Null characters are not allowed')
        return value


class UserProfile(ProfileFields):
    id: UUID


class RegisterResponse(BaseModel):
    user_id: UUID


class LoginRequest(BaseModel):
    model_config = ConfigDict(extra='forbid')
    id: UUID
    password: Password


class TokenResponse(BaseModel):
    token: str


class ErrorResponse(BaseModel):
    message: str
