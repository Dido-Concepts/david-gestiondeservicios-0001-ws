from dataclasses import dataclass
from typing import Optional


@dataclass
class UserAuth:
    iss: Optional[str] = None
    azp: Optional[str] = None
    aud: Optional[str] = None
    sub: Optional[str] = None
    email: Optional[str] = None
    email_verified: Optional[bool] = None
    at_hash: Optional[str] = None
    name: Optional[str] = None
    picture: Optional[str] = None
    given_name: Optional[str] = None
    family_name: Optional[str] = None
    iat: Optional[int] = None
    exp: Optional[int] = None
