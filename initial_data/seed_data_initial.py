import logging
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import SessionLocal
from sqlalchemy.future import select

from app.modules.user.infra.migration.models import (
    Roles,
    Accions,
    Pages,
    Users,
    UserRoles,
    Permissions,
)

logging.basicConfig(level=logging.INFO)


async def init_db(db: AsyncSession) -> None:
    try:
        # Comprobar si ya existe el rol "admin"
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

        # Inserción de acciones
        actions = ["create", "update", "delete", "find", "find_all"]
        for action in actions:
            result = await db.execute(select(Accions).filter(Accions.name == action))
            if not result.scalars().first():
                new_action = Accions(name=action, description=f"Permiso para {action}")
                db.add(new_action)
                logging.info(f"Acción '{action}' ha sido insertada.")
        await db.commit()

        # Inserción de páginas
        pages = ["dashboard", "user"]
        for page in pages:
            result = await db.execute(select(Pages).filter(Pages.name == page))
            if not result.scalars().first():
                new_page = Pages(name=page, description=f"Pagina {page}")
                db.add(new_page)
                logging.info(f"Página '{page}' ha sido insertada.")
        await db.commit()

        # Comprobar si ya existe el usuario "Esteban Villantoy"
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

            # Asignar el rol 'admin' al usuario
            result = await db.execute(select(Roles).filter(Roles.name == "admin"))
            admin_role_lookup = result.scalars().first()
            if admin_role_lookup:
                user_role = UserRoles(user_id=new_user.id, role_id=admin_role_lookup.id)
                db.add(user_role)
                await db.commit()
                logging.info("Rol 'admin' asignado al usuario 'Esteban Villantoy'.")

                # Asignar permisos para la página 'dashboard'
                result = await db.execute(
                    select(Pages).filter(Pages.name == "dashboard")
                )
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
            logging.info(
                "Usuario 'Esteban Villantoy' ya existe, no se realizó inserción."
            )
    except Exception as e:
        await db.rollback()
        logging.error(f"Error durante la inicialización de la base de datos: {e}")
    finally:
        await db.close()


if __name__ == "__main__":
    import asyncio

    async def main() -> None:
        async with SessionLocal() as db:
            await init_db(db)

    asyncio.run(main())
