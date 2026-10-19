from uuid import UUID, uuid4

import psycopg
from psycopg.rows import dict_row

from app.schemas import RegisterRequest


def connect_db() -> psycopg.Connection:
    return psycopg.connect(connect_timeout=3, row_factory=dict_row, options='-c timezone=UTC')


def create_user(data: RegisterRequest, password_hash: str) -> UUID:
    user_id = uuid4()
    with connect_db() as connection:
        connection.execute(
            '''INSERT INTO users
               (id, first_name, second_name, birthdate, gender, biography, city, password_hash)
               VALUES (%s, %s, %s, %s, %s, %s, %s, %s)''',
            (user_id, data.first_name, data.second_name, data.birthdate, data.gender,
             data.biography, data.city, password_hash),
        )
    return user_id


def get_user(user_id: UUID) -> dict | None:
    with connect_db() as connection:
        return connection.execute(
            '''SELECT id, first_name, second_name, birthdate, gender, biography, city
               FROM users WHERE id = %s''', (user_id,),
        ).fetchone()


def get_credentials(user_id: UUID) -> dict | None:
    with connect_db() as connection:
        return connection.execute(
            'SELECT id, password_hash FROM users WHERE id = %s', (user_id,),
        ).fetchone()


def create_session(user_id: UUID, token_hash: str, ttl_seconds: int) -> None:
    with connect_db() as connection:
        connection.execute(
            '''INSERT INTO sessions (token_hash, user_id, expires_at)
               VALUES (%s, %s, CURRENT_TIMESTAMP + %s * INTERVAL '1 second')''',
            (token_hash, user_id, ttl_seconds),
        )
