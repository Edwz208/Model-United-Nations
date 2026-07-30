# app/core/exceptions.py

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
import logging

logger = logging.getLogger(__name__)


class AppException(Exception):
    def __init__(self, detail: str = "An error occurred", status_code: int = 500, code: str = "internal_error"):
        self.detail = detail
        self.status_code = status_code
        self.code = code
        super().__init__(detail)

# --------------------------
# Generic Exceptions
# --------------------------

class NotFoundException(AppException):
    def __init__(self, detail="Resource not found"):
        super().__init__(detail, 404, "not_found")


class ConflictException(AppException):
    def __init__(self, detail="Conflict"):
        super().__init__(detail, 409, "conflict")


class ValidationException(AppException):
    def __init__(self, detail="Validation failed"):
        super().__init__(detail, 422, "validation_error")


class AuthorizationException(AppException):
    def __init__(self, detail="Forbidden"):
        super().__init__(detail, 403, "forbidden")


# --------------------------
# User Exceptions
# --------------------------

class UserNotFoundException(NotFoundException):
    def __init__(self, email: str | None = None, id: int | None = None):
        if email:
            detail = f"User not found with email '{email}'"
        elif id:
            detail = f"User not found with id {id}"
        else:
            detail = "User not found"

        super().__init__(detail)


class UserAlreadyExistsException(ConflictException):
    def __init__(self, email: str):
        super().__init__(f"User already exists with email '{email}'")


class EmailAlreadyExistsException(ConflictException):
    def __init__(self, email: str):
        super().__init__(f"Email already exists '{email}'")


# --------------------------
# Domain Exceptions
# --------------------------

class CountryNotFoundException(NotFoundException):
    def __init__(self, country_id: int | None = None):
        detail = f"Country with id {country_id} was not found" if country_id is not None else "Country not found"
        super().__init__(detail)


class CouncilNotFoundException(NotFoundException):
    def __init__(self, council_id: int | None = None):
        detail = f"Council with id {council_id} was not found" if council_id is not None else "Council not found"
        super().__init__(detail)


class ResolutionNotFoundException(NotFoundException):
    def __init__(self, resolution_id: int | None = None):
        detail = f"Resolution with id {resolution_id} was not found" if resolution_id is not None else "Resolution not found"
        super().__init__(detail)


class AmendmentNotFoundException(NotFoundException):
    def __init__(self, amendment_id: int | None = None):
        detail = f"Amendment with id {amendment_id} was not found" if amendment_id is not None else "Amendment not found"
        super().__init__(detail)


class SecretariatNotFoundException(NotFoundException):
    def __init__(self, secretariat_id: int | None = None):
        detail = f"Secretariat member with id {secretariat_id} was not found" if secretariat_id is not None else "Secretariat member not found"
        super().__init__(detail)


class InvalidCredentialsException(AuthorizationException):
    def __init__(self):
        super().__init__("Invalid credentials")


class RefreshTokenMissingException(AuthorizationException):
    def __init__(self):
        super().__init__("Missing refresh token")


class InvalidSpreadsheetException(ValidationException):
    def __init__(self, detail: str = "Invalid spreadsheet url"):
        super().__init__(detail)


class InvalidUploadException(ValidationException):
    def __init__(self, detail: str = "Invalid upload"):
        super().__init__(detail)


class InvalidAssignmentException(ValidationException):
    def __init__(self, detail: str = "Submitter, seconder or negator not valid for this council"):
        super().__init__(detail)


def register_exception_handlers(app: FastAPI):

    @app.exception_handler(AppException)
    async def app_exception_handler(request: Request, exc: AppException):
        logger.exception("AppException occurred: %s", exc.detail)
        return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})

    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):
        logger.exception("HTTPException occurred: %s", exc.detail)
        if exc.status_code == 401:
            return JSONResponse(status_code=401, content={ "detail": "Authentication failed."})

        if exc.status_code == 403:
            return JSONResponse(status_code=403, content={"detail": "You do not have permission to access this resource."})
        # Any other HTTPException
        return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})

    @app.exception_handler(Exception)
    async def unexpected_exception_handler(request: Request, exc: Exception):
        logger.exception("Unexpected error occurred: %s", exc)
        return JSONResponse(status_code=500, content={"detail": "Internal Server Error"})