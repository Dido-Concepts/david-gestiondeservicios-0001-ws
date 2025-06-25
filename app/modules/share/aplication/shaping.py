from typing import Optional, List, Dict, Any, Set
from dataclasses import is_dataclass, asdict

# Asumimos que esta excepción personalizada está definida en un archivo compartido de excepciones
from app.modules.share.domain.exceptions import InvalidFieldsException

class DataShaper:
    """
    Servicio reutilizable y especializado en la transformación de datos (shaping).
    Su responsabilidad es tomar una lista de datos y moldearla según los campos
    solicitados por el cliente, aplicando validaciones en el proceso.
    """
    def shape_data(
        self,
        data: List[Any],
        fields: Optional[str],
        allowed_fields: Set[str],
        required_fields: Set[str]
    ) -> List[Dict[str, Any]]:
        """
        Filtra una lista de objetos (ej. dataclasses) para devolver solo los campos deseados.

        Args:
            data: La lista de objetos (ej. CustomerEntity) obtenida del repositorio.
            fields: El string con los campos solicitados por el cliente (ej: "id,name,status").
            allowed_fields: Un conjunto con todos los nombres de campos válidos para este recurso.
            required_fields: Un conjunto de campos que siempre deben ser incluidos en la respuesta.

        Returns:
            Una nueva lista de diccionarios con la forma final solicitada.

        Raises:
            InvalidFieldsException: Si el cliente solicita un campo que no existe en allowed_fields.
        """
        # Si no hay datos, devolvemos una lista vacía.
        if not data:
            return []

        # Convertimos la lista de objetos (dataclasses) a una lista de diccionarios
        # para poder manipular las claves de forma genérica.
        if data and is_dataclass(data[0]):
            dict_data = [asdict(item) for item in data]
        else:
            dict_data = data  # Asumimos que ya son diccionarios

        # Si el cliente no especifica campos, devolvemos los objetos completos.
        if not fields:
            return dict_data

        # Procesamos los campos solicitados por el cliente.
        requested_fields = {field.strip() for field in fields.split(',')}

        # --- Validación ---
        # Comparamos los campos solicitados con los permitidos para este modelo.
        invalid_fields = requested_fields - allowed_fields
        if invalid_fields:
            # Si se encuentra algún campo inválido, lanzamos un error específico
            # que será capturado por el manejador de excepciones de FastAPI.
            raise InvalidFieldsException(f"Los siguientes campos no son válidos: {', '.join(sorted(invalid_fields))}")

        # --- Regla de Negocio ---
        # Aseguramos que los campos requeridos siempre estén en la respuesta final.
        final_fields = requested_fields.union(required_fields)

        # Construimos la respuesta final, incluyendo solo los campos solicitados y requeridos.
        return [
            {key: row[key] for key in final_fields if key in row}
            for row in dict_data
        ]