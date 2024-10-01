import logging
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.database import SessionLocal
from app.modules.user.infra.migration.models import (
    Accions,
    Permissions,
    Roles,
    UserRoles,
    Users,
)

logging.basicConfig(level=logging.INFO)


def make_naive(dt: datetime) -> datetime:
    """Convierte un datetime con zona horaria a naive datetime."""
    return dt.replace(tzinfo=None) if dt.tzinfo else dt


async def init_db(db: AsyncSession) -> None:
    try:
        await insert_roles(db)
        await insert_actions(db)
        await insert_user_and_permissions(db)
    except Exception as e:
        await db.rollback()
        logging.error(f"Error durante la inicialización de la base de datos: {e}")
    finally:
        await db.close()


async def insert_roles(db: AsyncSession) -> None:
    result = await db.execute(select(Roles).filter(Roles.name == "admin"))
    if not result.scalars().first():
        now = make_naive(datetime.utcnow())
        admin_role = Roles(
            name="admin", description="Administrator", created_at=now, updated_at=now
        )
        supervisor_role = Roles(
            name="supervisor", description="Supervisor", created_at=now, updated_at=now
        )
        db.add_all([admin_role, supervisor_role])
        await db.commit()
        logging.info("Roles 'admin' y 'supervisor' han sido insertados.")
    else:
        logging.info("Roles ya existen, no se realizó inserción.")


async def insert_actions(db: AsyncSession) -> None:
    # Acciones que se desean agregar a la base de datos
    actions = {
        "user:list_users": "Permiso para listar todos los usuarios.",
        "user:create_user": "Permiso para crear nuevos usuarios en el sistema.",
        "user:edit_user": "Permiso para editar la información de los usuarios.",
        "user:change_status_user": "Permiso para cambiar el estado activo/inactivo de los usuarios.",
        "role:list_roles": "Permiso para listar todos los roles.",
        "role:create_role": "Permiso para crear nuevos roles en el sistema.",
    }

    # Obtener las acciones ya existentes en la base de datos
    existing_actions_result = await db.execute(select(Accions.name))
    existing_actions = set(
        existing_actions_result.scalars().all()
    )  # Convertir a set para búsqueda rápida

    new_action_ids = (
        []
    )  # Lista para almacenar los IDs de las acciones nuevas insertadas
    now = make_naive(datetime.utcnow())  # Obtener la fecha y hora actual

    # Insertar solo las acciones nuevas
    for action, description in actions.items():
        if action not in existing_actions:
            new_action = Accions(
                name=action, description=description, created_at=now, updated_at=now
            )
            db.add(new_action)
            await db.flush()
            new_action_ids.append(new_action.id)
            logging.info(
                f"Acción '{action}' ha sido insertada con la descripción: '{description}'."
            )
        else:
            logging.info(f"Acción '{action}' ya existe en la base de datos.")

    # Confirmar los cambios de las acciones nuevas
    await db.commit()

    # Relacionar las nuevas acciones con el rol 'admin'
    if new_action_ids:
        result = await db.execute(select(Roles).filter(Roles.name == "admin"))
        admin_role = result.scalars().first()
        if admin_role:
            # Crear las relaciones Permissions solo para las acciones nuevas
            permissions = [
                Permissions(role_id=admin_role.id, accion_id=action_id)
                for action_id in new_action_ids
            ]
            db.add_all(permissions)
            await db.commit()
            logging.info(
                "Todas las acciones nuevas han sido vinculadas con el rol 'admin'."
            )
        else:
            logging.warning("No se encontró el rol 'admin', no se crearon permisos.")
    else:
        logging.info(
            "No se encontraron nuevas acciones para asociar con el rol 'admin'."
        )


async def insert_user_and_permissions(db: AsyncSession) -> None:
    result = await db.execute(
        select(Users).filter(Users.user_name == "Esteban Villantoy")
    )
    if not result.scalars().first():
        now = make_naive(datetime.utcnow())
        new_user = Users(
            user_name="Esteban Villantoy",
            email="villantoyesteban@gmail.com",
            created_at=now,
            updated_at=now,
        )
        db.add(new_user)
        await db.commit()
        logging.info("Usuario 'Esteban Villantoy' ha sido insertado.")

        result = await db.execute(select(Roles).filter(Roles.name == "admin"))
        admin_role_lookup = result.scalars().first()
        if admin_role_lookup:
            user_role = UserRoles(user_id=new_user.id, role_id=admin_role_lookup.id)
            db.add(user_role)
            await db.commit()
            logging.info("Rol 'admin' asignado al usuario 'Esteban Villantoy'.")
    else:
        logging.info("Usuario 'Esteban Villantoy' ya existe, no se realizó inserción.")


if __name__ == "__main__":
    import asyncio

    async def main() -> None:
        async with SessionLocal() as db:
            await init_db(db)

    asyncio.run(main())
