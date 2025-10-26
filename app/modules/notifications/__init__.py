# Importar todos los handlers para asegurar que se registren en MediatR
# Esto es importante para que los handlers estén disponibles cuando se use el mediator

from app.modules.notifications.application.commands.deactivate_notification_location.deactivate_notification_location_command_handler import (
    DeactivateNotificationLocationCommandHandler,
)

# Command Handlers
from app.modules.notifications.application.commands.send_appointment_notifications.send_appointment_notifications_command_handler import (
    SendAppointmentNotificationsCommandHandler,
)
from app.modules.notifications.application.commands.upsert_notification_location.upsert_notification_location_command_handler import (
    UpsertNotificationLocationCommandHandler,
)
from app.modules.notifications.application.queries.get_active_notification_locations.get_active_notification_locations_query_handler import (
    GetActiveNotificationLocationsQueryHandler,
)

# Query Handlers
from app.modules.notifications.application.queries.get_all_locations_notification_status.get_all_locations_notification_status_query_handler import (
    GetAllLocationsNotificationStatusQueryHandler,
)

__all__ = [
    "SendAppointmentNotificationsCommandHandler",
    "UpsertNotificationLocationCommandHandler",
    "DeactivateNotificationLocationCommandHandler",
    "GetAllLocationsNotificationStatusQueryHandler",
    "GetActiveNotificationLocationsQueryHandler",
]
