import logging
from uuid import UUID
import psycopg
from fastapi import FastAPI, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.openapi.utils import get_openapi
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
from app import db, security
from app.config import Settings
from app.schemas import (
    ErrorResponse, LoginRequest, RegisterRequest, RegisterResponse, TokenResponse, UserProfile,
)

logger = logging.getLogger(__name__)


def create_app() -> FastAPI:
    application = FastAPI(
        title='Social Network Homework', version='1.0.0',
        description='Регистрация, вход и публичные анкеты. Токен для чтения не требуется.',
    )
    application.state.settings = Settings.from_env()

    @application.exception_handler(RequestValidationError)
    async def validation_error(request, exc):
        # Never echo request input: it may contain a password.
        return JSONResponse(status_code=400, content={'message': 'Невалидные данные'})

    @application.exception_handler(StarletteHTTPException)
    async def http_error(request, exc):
        return JSONResponse(status_code=exc.status_code, content={'message': str(exc.detail)})

    @application.exception_handler(psycopg.OperationalError)
    @application.exception_handler(psycopg.InterfaceError)
    async def unavailable_database(request, exc):
        logger.error('Database unavailable (%s)', type(exc).__name__)
        return JSONResponse(status_code=503, content={'message': 'База данных недоступна'})

    @application.exception_handler(Exception)
    async def unexpected_error(request, exc):
        logger.error('Unexpected application error (%s)', type(exc).__name__)
        return JSONResponse(status_code=500, content={'message': 'Внутренняя ошибка сервера'})

    errors = {code: {'model': ErrorResponse} for code in (400, 404, 500, 503)}

    @application.post('/user/register', response_model=RegisterResponse, responses=errors)
    def register(data: RegisterRequest):
        password_hash = security.hash_password(data.password.get_secret_value())
        return {'user_id': db.create_user(data, password_hash)}

    @application.get('/user/get/{id}', response_model=UserProfile, responses=errors)
    def get_profile(id: UUID):
        user = db.get_user(id)
        if user is None:
            raise HTTPException(404, 'Анкета не найдена')
        return user

    @application.post('/login', response_model=TokenResponse,
                      responses={**errors, 401: {'model': ErrorResponse}})
    def login(data: LoginRequest):
        user = db.get_credentials(data.id)
        if user is None:
            raise HTTPException(404, 'Пользователь не найден')
        if not security.verify_password(data.password.get_secret_value(), user['password_hash']):
            raise HTTPException(401, 'Неверный пароль')
        token, token_hash = security.issue_token()
        db.create_session(data.id, token_hash, application.state.settings.session_ttl_seconds)
        return {'token': token}

    @application.get('/health', responses={503: {'model': ErrorResponse}})
    def health():
        with db.connect_db() as connection:
            connection.execute('SELECT 1')
        return {'status': 'ok'}

    def openapi_schema():
        if application.openapi_schema is None:
            schema = get_openapi(title=application.title, version=application.version,
                                 description=application.description, routes=application.routes)
            # RequestValidationError is deliberately mapped to 400, not 422.
            for path in schema['paths'].values():
                for operation in path.values():
                    if isinstance(operation, dict):
                        operation.get('responses', {}).pop('422', None)
            application.openapi_schema = schema
        return application.openapi_schema

    application.openapi = openapi_schema

    return application


app = create_app()
