"""Provision or rotate local Day 2 database access without resetting data."""

import argparse
import json
import os
import secrets
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATABASES = (
    ("bankflow", "bankflow_user", ".env"),
    ("bankflow_test", "bankflow_test_user", ".env.test"),
)


def render_environment(template: str, database: str, user: str, password: str) -> str:
    """Render one local environment file without exposing its password."""
    content = template.replace("POSTGRES_DB=bankflow\n", f"POSTGRES_DB={database}\n")
    content = content.replace("POSTGRES_USER=bankflow_user\n", f"POSTGRES_USER={user}\n")
    content = content.replace("POSTGRES_PASSWORD=\n", f"POSTGRES_PASSWORD={password}\n")
    if database == "bankflow_test":
        content = content.replace("APP_ENV=development", "APP_ENV=test")
    return content


def replace_environment_setting(content: str, name: str, value: str) -> str:
    """Replace exactly one setting while preserving every other local choice."""
    prefix = name + "="
    replaced = 0
    lines = []
    for line in content.splitlines(keepends=True):
        if line.startswith(prefix):
            ending = "\r\n" if line.endswith("\r\n") else "\n" if line.endswith("\n") else ""
            line = prefix + value + ending
            replaced += 1
        lines.append(line)
    if replaced != 1:
        raise ValueError(f"Expected exactly one {name} setting.")
    return "".join(lines)


def admin_sql(database: str, statement: str) -> str:
    result = subprocess.run(
        [
            "docker",
            "exec",
            "-i",
            "-u",
            "datalab",
            "bankflow",
            "psql",
            "-X",
            "-w",
            "-h",
            "/home/datalab/runtime/postgres",
            "-U",
            "datalab",
            "-d",
            database,
            "-v",
            "ON_ERROR_STOP=1",
            "-Atq",
        ],
        input=statement,
        capture_output=True,
        text=True,
        timeout=30,
        check=False,
    )
    if result.returncode:
        # psql errors can contain the submitted SQL, including a generated password.
        raise RuntimeError("Local database administration failed; raw SQL/errors are suppressed.")
    return result.stdout.strip()


def verify_local_superuser() -> None:
    if admin_sql("postgres", "SELECT rolsuper FROM pg_roles WHERE rolname=current_user;") != "t":
        raise RuntimeError("Provisioning requires the lab's local database superuser.")


def rotate_passwords() -> int:
    """Rotate both owner passwords and atomically replace their ignored files."""
    try:
        if not all((ROOT / filename).exists() for _, _, filename in DATABASES):
            raise RuntimeError("Both local environment files are required for rotation.")
        state = json.loads(
            admin_sql(
                "postgres",
                "SELECT json_build_object('databases', (SELECT count(*) FROM pg_database "
                "WHERE datname IN ('bankflow', 'bankflow_test')), 'roles', "
                "(SELECT count(*) FROM pg_roles WHERE rolname IN "
                "('bankflow_user', 'bankflow_test_user')));",
            )
        )
        if state != {"databases": 2, "roles": 2}:
            raise RuntimeError("Expected BankFlow databases and roles were not found.")
        verify_local_superuser()
        credentials = {name: secrets.token_urlsafe(32) for name, _, _ in DATABASES}
        pending = []
        for database, user, filename in DATABASES:
            path = ROOT / filename
            temporary = path.with_name(path.name + ".next")
            current = path.read_text(encoding="utf-8")
            updated = replace_environment_setting(
                current, "POSTGRES_PASSWORD", credentials[database]
            )
            with temporary.open("x", encoding="utf-8", newline="\n") as file:
                file.write(updated)
            pending.append((temporary, path))
        statements = ["BEGIN;"]
        for database, user, _ in DATABASES:
            statements.append(f"ALTER ROLE {user} PASSWORD '{credentials[database]}';")
        statements.append("COMMIT;")
        admin_sql("postgres", "\n".join(statements))
        for temporary, path in pending:
            os.replace(temporary, path)
        print("Rotated both local database owner passwords.")
        print("Credentials remain only in ignored .env and .env.test files.")
        return 0
    except (RuntimeError, OSError, subprocess.SubprocessError, ValueError) as exc:
        print(
            str(exc) if isinstance(exc, RuntimeError) else "Rotation failed; inspect local setup."
        )
        print("No database or role was reset; retain any ignored .env*.next recovery files.")
        return 1


def provision() -> int:
    try:
        if any((ROOT / filename).exists() for _, _, filename in DATABASES):
            raise RuntimeError("Local environment files already exist; nothing was changed.")
        state = admin_sql(
            "postgres",
            "SELECT json_build_object('databases', (SELECT count(*) FROM pg_database "
            "WHERE datname IN ('bankflow', 'bankflow_test')), 'roles', "
            "(SELECT count(*) FROM pg_roles WHERE rolname IN "
            "('bankflow_user', 'bankflow_test_user')));",
        )
        if any(json.loads(state).values()):
            raise RuntimeError("BankFlow databases or roles already exist; nothing was changed.")
        verify_local_superuser()
        template = (ROOT / ".env.example").read_text(encoding="utf-8")
        credentials = {name: secrets.token_urlsafe(32) for name, _, _ in DATABASES}
        # Persist locally before creating roles so a partial failure cannot lose the passwords.
        for database, user, filename in DATABASES:
            content = render_environment(template, database, user, credentials[database])
            with (ROOT / filename).open("x", encoding="utf-8", newline="\n") as file:
                file.write(content)
        for database, user, _ in DATABASES:
            # Names are fixed constants and token_urlsafe passwords contain no SQL quotes.
            admin_sql(
                "postgres",
                f"CREATE ROLE {user} LOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE "
                f"NOREPLICATION NOBYPASSRLS PASSWORD '{credentials[database]}';\n"
                f"CREATE DATABASE {database} OWNER {user};\n"
                f"REVOKE ALL ON DATABASE {database} FROM PUBLIC;\n",
            )
            admin_sql(
                database,
                "REVOKE CREATE ON SCHEMA public FROM PUBLIC;\n"
                f"GRANT USAGE, CREATE ON SCHEMA public TO {user};\n",
            )
        print("Created bankflow and bankflow_test with separate non-superuser owner roles.")
        print("Credentials are stored only in ignored .env and .env.test files.")
        return 0
    except (RuntimeError, OSError, subprocess.SubprocessError, ValueError) as exc:
        print(
            str(exc)
            if isinstance(exc, RuntimeError)
            else "Provisioning failed; inspect local setup."
        )
        print("Existing resources are never reset. Retain any generated local credential files.")
        return 1


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--rotate-passwords",
        action="store_true",
        help="rotate existing local application/test passwords without changing data",
    )
    args = parser.parse_args()
    return rotate_passwords() if args.rotate_passwords else provision()


if __name__ == "__main__":
    raise SystemExit(main())
