"""
Este módulo contiene las excepciones personalizadas del dominio compartido,
utilizadas a través de diferentes módulos de la aplicación para manejar
errores de negocio o de validación de forma estandarizada.
"""

class InvalidFieldsException(ValueError):
    """
    Excepción lanzada cuando un cliente de la API solicita uno o más campos
    que no son válidos o no están permitidos para un recurso específico.

    Hereda de ValueError, ya que representa un error en el valor de los
    parámetros de la solicitud.
    """
    pass

# Puedes añadir más excepciones compartidas aquí en el futuro.
# Por ejemplo:
#
# class BusinessRuleException(Exception):
#     """Excepción para violaciones de reglas de negocio generales."""
#     pass
#