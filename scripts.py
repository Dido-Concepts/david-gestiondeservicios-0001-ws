import subprocess

import click


def format() -> None:
    subprocess.run(["black", "."])


def lint() -> None:
    subprocess.run(["flake8"])


def typecheck() -> None:
    subprocess.run(["mypy", "."])


def dev() -> None:
    subprocess.run(["fastapi", "dev", "app/main.py"])


@click.command()
@click.argument("message")
def migrations(message: str) -> None:
    try:
        subprocess.run(
            ["alembic", "revision", "--autogenerate", "-m", message],
            check=True,
        )

        subprocess.run(["alembic", "upgrade", "head"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error ejecutando el comando: {e}")


def seed_initial_data() -> None:
    subprocess.run(["py", "initial_data/seed_data_initial.py"])
