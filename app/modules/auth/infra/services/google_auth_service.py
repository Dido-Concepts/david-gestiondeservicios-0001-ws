from typing import Any

from google.auth.transport import requests as google_requests
from google.oauth2 import id_token

from app.modules.auth.domain.models.user_auth_domain import UserAuth


class GoogleAuthService:
    def __init__(self, client_id: str) -> None:
        self.client_id = client_id

    def verify_token(self, token: str) -> UserAuth:
        try:
            request = google_requests.Request()  # type: ignore

            id_info: dict[str, Any] = id_token.verify_oauth2_token(
                token, request, self.client_id  # type: ignore
            )

            if id_info["aud"] != self.client_id:
                raise ValueError("El token no es para esta aplicación")

            user = UserAuth(
                iss=id_info.get("iss", ""),
                azp=id_info.get("azp", ""),
                aud=id_info.get("aud", ""),
                sub=id_info.get("sub", ""),
                email=id_info.get("email", ""),
                email_verified=id_info.get("email_verified", False),
                at_hash=id_info.get("at_hash", ""),
                name=id_info.get("name", ""),
                picture=id_info.get("picture", ""),
                given_name=id_info.get("given_name", ""),
                family_name=id_info.get("family_name", ""),
                iat=id_info.get("iat", 0),
                exp=id_info.get("exp", 0),
            )

            return user

        except ValueError:
            raise Exception("Token de autenticación inválido")
