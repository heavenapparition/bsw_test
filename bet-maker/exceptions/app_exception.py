import logging
from enum import Enum
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


class ErrorType(str, Enum):
    NOT_FOUND = "not_found"
    VALIDATION_ERROR = "validation_error"
    BUSINESS_RULE_VIOLATION = "business_rule_violation"
    SYSTEM_ERROR = "system_error"


class ApplicationException(Exception):
    def __init__(
        self, type_: ErrorType, message: str, details: Optional[Dict[str, Any]] = None
    ):
        self.type = type_
        self.message = message
        self.details = details or {}
        logger.error(f"{type_}: {message} - {details}")
