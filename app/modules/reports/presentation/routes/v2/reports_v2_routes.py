from typing import Annotated

from fastapi import APIRouter, Depends
from mediatr import Mediator
from fastapi.responses import StreamingResponse

from app.modules.auth.presentation.dependencies.auth_dependencies import (
    permission_required,
)
from app.modules.reports.application.queries.get_reports_excel.get_reports_excel_handler import (
    GetReportsExcelQuery,
)


class ReportsV2Controller:
    def __init__(self, mediator: Mediator):
        self.mediator = mediator
        self.router = APIRouter()
        self._add_routes()

    def _add_routes(self) -> None:
        self.router.get(
            "/reports/excel",
            dependencies=[Depends(permission_required(roles=["admin", "staff"]))],
            responses={
                200: {
                    "description": "Devuelve un archivo Excel con los reportes filtrados",
                    "content": {"application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": {}}
                }
            },
        )(self.get_reports_excel)

    async def get_reports_excel(
        self,
        query: Annotated[GetReportsExcelQuery, Depends()],
    ) -> StreamingResponse:
        """
        Genera y devuelve un archivo Excel con los reportes filtrados por fecha y barbero.
        """
        excel_buffer = await self.mediator.send_async(query)

        # Resetear el puntero del buffer al inicio
        excel_buffer.seek(0)
        
        # Crear el StreamingResponse con el BytesIO
        response = StreamingResponse(
            excel_buffer,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
        response.headers["Content-Disposition"] = "attachment; filename=reportes_citas.xlsx"
        return response
