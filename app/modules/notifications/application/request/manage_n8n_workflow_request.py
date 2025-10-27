from pydantic import BaseModel


class ManageN8nWorkflowRequest(BaseModel):
    """
    Request para activar o desactivar el workflow de N8N
    """

    activate: bool  # True para activar, False para desactivar
