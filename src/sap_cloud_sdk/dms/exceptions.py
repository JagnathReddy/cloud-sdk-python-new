from typing import Optional

class DmsException(Exception):
    """Base exception for all DMS SDK errors."""

    def __init__(
        self,
        message: Optional[str] = None,
        status_code: Optional[int] = None,
        error_content: Optional[str] = None,
        cause: Optional[Exception] = None,
    ) -> None:
        super().__init__(message if message is not None else "")
        self.status_code = status_code
        self.error_content = error_content
        if cause is not None:
            self.__cause__ = cause

    def __repr__(self) -> str:
        return f"DmsException(status_code={self.status_code}, message={str(self)!r})"