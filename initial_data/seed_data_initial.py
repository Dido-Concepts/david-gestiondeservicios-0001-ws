import logging

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.database import SessionLocal
from app.modules.user.infra.migration.models import (
    Accions,
    Pages,
    Permissions,
    Roles,
    UserRoles,
    Users,
)

logging.basicConfig(level=logging.INFO)


async def init_db(db: AsyncSession) -> None:
    try:
        await insert_roles(db)
        await insert_actions(db)
        await insert_pages(db)
        await insert_user_and_permissions(db)
    except Exception as e:
        await db.rollback()
        logging.error(f"Error durante la inicialización de la base de datos: {e}")
    finally:
        await db.close()


async def insert_roles(db: AsyncSession) -> None:
    result = await db.execute(select(Roles).filter(Roles.name == "admin"))
    if not result.scalars().first():
        admin_role = Roles(name="admin", description="Administrator")
        supervisor_role = Roles(name="supervisor", description="Supervisor")
        public_role = Roles(name="public", description="Publico")
        db.add_all([admin_role, supervisor_role, public_role])
        await db.commit()
        logging.info("Roles 'admin', 'supervisor', y 'public' han sido insertados.")
    else:
        logging.info("Roles ya existen, no se realizó inserción.")


async def insert_actions(db: AsyncSession) -> None:
    actions = ["create", "update", "delete", "find", "find_all"]
    for action in actions:
        result = await db.execute(select(Accions).filter(Accions.name == action))
        if not result.scalars().first():
            new_action = Accions(name=action, description=f"Permiso para {action}")
            db.add(new_action)
            logging.info(f"Acción '{action}' ha sido insertada.")
    await db.commit()


async def insert_pages(db: AsyncSession) -> None:
    pages = ["dashboard"]
    for page in pages:
        result = await db.execute(select(Pages).filter(Pages.name == page))
        if not result.scalars().first():
            new_page = Pages(name=page, description=f"Pagina {page}")
            db.add(new_page)
            logging.info(f"Página '{page}' ha sido insertada.")
    await db.commit()


async def insert_user_and_permissions(db: AsyncSession) -> None:
    result = await db.execute(
        select(Users).filter(Users.user_name == "Esteban Villantoy")
    )
    if not result.scalars().first():
        new_user = Users(
            user_name="Esteban Villantoy",
            email="villantoyesteban@gmail.com",
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

            result = await db.execute(select(Pages).filter(Pages.name == "dashboard"))
            dashboard_page = result.scalars().first()
            if dashboard_page:
                actions_2 = (await db.execute(select(Accions))).scalars().all()
                for action in actions_2:
                    permission = Permissions(
                        role_id=admin_role_lookup.id,
                        accion_id=action.id,
                        page_id=dashboard_page.id,
                    )
                    db.add(permission)
                await db.commit()
                logging.info(
                    "Permisos asignados al rol 'admin' para la página 'dashboard'."
                )
    else:
        logging.info("Usuario 'Esteban Villantoy' ya existe, no se realizó inserción.")


if __name__ == "__main__":
    import asyncio

    async def main() -> None:
        async with SessionLocal() as db:
            await init_db(db)

    asyncio.run(main())
