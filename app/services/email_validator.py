import re
from .utils import is_domain_valid
from .utils import is_disposable
from .schemas import EmailResponse


class EmailFormatError(Exception):
    """Raised when the email format is invalid."""


class DisposableEmailError(Exception):
    """Raised when the email domain is disposable."""


class EmailMXRecordError(Exception):
    """Raised when the email domain has no valid MX records."""


class EmailValidator:
    """Class-based email validation service."""

    def __init__(self, email: str):
        self.email = email
        self.domain = email.split("@")[-1]

    @staticmethod
    def check_email_pattern(email: str) -> bool:
        """Check if the email matches the correct pattern using regex."""
        return bool(
            re.match(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$", email.strip())
        )

    def validate(self) -> EmailResponse:
        """Validate the email format, disposable domain, and MX record."""

        if not self.check_email_pattern(self.email):
            raise EmailFormatError("Invalid email format.")

        if is_disposable(self.domain):
            raise DisposableEmailError("Disposable email addresses are not allowed.")

        if not is_domain_valid(self.domain):
            raise EmailMXRecordError("Domain has no valid MX records.")

        return EmailResponse(email=self.email, is_valid=True, message="Email is valid.")

    def check_disposable(self) -> EmailResponse:
        """Check if the email domain is disposable."""
        disposable = is_disposable(self.domain)
        return EmailResponse(
            email=self.email,
            is_valid=not disposable,
            message="Domain is disposable."
            if disposable
            else "Domain is not disposable.",
        )

    def check_mx_record(self) -> EmailResponse:
        """Check if the email domain has valid MX records."""
        has_mx = is_domain_valid(self.domain)
        return EmailResponse(
            email=self.email,
            is_valid=has_mx,
            message="Valid MX records found." if has_mx else "No valid MX records.",
        )
