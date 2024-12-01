from fastapi import Request, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from .app_exception import ApplicationException, ErrorType

error_type_to_status_code = {
    ErrorType.NOT_FOUND: status.HTTP_404_NOT_FOUND,
    ErrorType.VALIDATION_ERROR: status.HTTP_400_BAD_REQUEST,
    ErrorType.BUSINESS_RULE_VIOLATION: status.HTTP_400_BAD_REQUEST,
    ErrorType.SYSTEM_ERROR: status.HTTP_500_INTERNAL_SERVER_ERROR,
}


class ErrorHandlingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: callable):
        try:
            response = await call_next(request)
            return response
        except ApplicationException as exc:
            return JSONResponse(
                status_code=error_type_to_status_code.get(
                    exc.type, status.HTTP_500_INTERNAL_SERVER_ERROR
                ),
                content={
                    "error_type": exc.type,
                    "message": exc.message,
                    "details": exc.details,
                },
            )
        except Exception as exc:
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={
                    "error_type": ErrorCode.SYSTEM_ERROR,
                    "message": "Internal server error",
                    "details": {"error_name": str(type(exc).__name__)},
                },
            )
