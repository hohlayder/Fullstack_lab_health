from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

VALIDATION_MESSAGES = {
    "missing": "Обязательное поле",
    "extra_forbidden": "Неизвестное поле",
    "string_too_short": "Строка слишком короткая или пустая",
    "string_too_long": "Строка слишком длинная",
    "too_short": "Список должен содержать хотя бы одно значение",
    "too_long": "Слишком много значений",
    "uuid_parsing": "Некорректный UUID",
    "uuid_type": "Ожидается UUID",
    "bool_parsing": "Ожидается true или false",
    "date_from_datetime_parsing": "Некорректная дата, используйте YYYY-MM-DD",
    "date_parsing": "Некорректная дата, используйте YYYY-MM-DD",
    "time_parsing": "Некорректное время, используйте HH:MM",
    "greater_than_equal": "Значение меньше допустимого минимума",
    "less_than_equal": "Значение превышает допустимый максимум",
}


def register_error_handlers(app: FastAPI) -> None:
    @app.exception_handler(RequestValidationError)
    async def validation_error(_: Request, error: RequestValidationError):
        details = [
            {
                "loc": list(item["loc"]),
                "type": item["type"],
                "msg": VALIDATION_MESSAGES.get(
                    item["type"], item["msg"].removeprefix("Value error, ")
                ),
            }
            for item in error.errors()
        ]
        return JSONResponse(status_code=422, content={"detail": details})

    @app.exception_handler(IntegrityError)
    async def integrity_error(_: Request, error: IntegrityError):
        constraint = getattr(getattr(error.orig, "diag", None), "constraint_name", "")
        message = (
            "Отметка для этого назначения, дня и времени уже существует"
            if constraint == "uq_intake_slot"
            else "Операция нарушает связи или ограничения данных"
        )
        return JSONResponse(status_code=409, content={"detail": message})

    @app.exception_handler(SQLAlchemyError)
    async def database_error(_: Request, __: SQLAlchemyError):
        return JSONResponse(
            status_code=503, content={"detail": "База данных недоступна. Повторите запрос позже."}
        )
