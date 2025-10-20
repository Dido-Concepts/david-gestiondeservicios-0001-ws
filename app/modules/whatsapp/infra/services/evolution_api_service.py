from typing import Any, Dict, Optional

import httpx

from config.setting import EVOLUTION_API_KEY, EVOLUTION_URL, INSTANCE_NAME


class EvolutionApiService:
    """
    Servicio para interactuar con Evolution API v2.
    Maneja el envío de mensajes de WhatsApp.
    """

    def __init__(self) -> None:
        """
        Inicializa el servicio con la configuración de Evolution API.
        """
        self.base_url = EVOLUTION_URL
        self.api_key = EVOLUTION_API_KEY
        self.instance_name = INSTANCE_NAME
        self.timeout = 30.0

    async def send_text_message(
        self,
        number: str,
        text: str,
        delay: Optional[int] = None,
        link_preview: Optional[bool] = True,
    ) -> Dict[str, Any]:
        """
        Envía un mensaje de texto a través de Evolution API.

        Args:
            number: Número de WhatsApp (con código de país)
            text: Texto del mensaje
            delay: Tiempo de espera en milisegundos antes de enviar
            link_preview: Si mostrar vista previa de enlaces

        Returns:
            Respuesta de Evolution API

        Raises:
            Exception: Si hay error en la comunicación con la API
        """
        url = f"{self.base_url}/message/sendText/{self.instance_name}"

        headers = {"Content-Type": "application/json", "apikey": self.api_key}

        payload: Dict[str, Any] = {
            "number": number,
            "text": text,
            "linkPreview": link_preview,
        }

        # Agregar delay si se especifica
        if delay is not None:
            payload["delay"] = delay

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(url=url, json=payload, headers=headers)

                # Verificar si la respuesta fue exitosa
                response.raise_for_status()

                return response.json()  # type: ignore[no-any-return]

        except httpx.TimeoutException:
            raise Exception("Timeout al conectar con Evolution API")
        except httpx.HTTPStatusError as e:
            error_detail = ""
            try:
                error_response = e.response.json()
                error_detail = error_response.get("message", str(e))
            except Exception:
                error_detail = str(e)
            raise Exception(f"Error HTTP {e.response.status_code}: {error_detail}")
        except httpx.RequestError as e:
            raise Exception(f"Error de conexión con Evolution API: {str(e)}")
        except Exception as e:
            raise Exception(f"Error inesperado: {str(e)}")

    async def get_instance_status(self) -> Dict[str, Any]:
        """
        Obtiene el estado de la instancia de WhatsApp.

        Returns:
            Estado de la instancia

        Raises:
            Exception: Si hay error en la comunicación con la API
        """
        url = f"{self.base_url}/instance/status/{self.instance_name}"

        headers = {"apikey": self.api_key}

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(url=url, headers=headers)
                response.raise_for_status()
                return response.json()  # type: ignore[no-any-return]

        except Exception as e:
            raise Exception(f"Error al obtener estado de instancia: {str(e)}")
