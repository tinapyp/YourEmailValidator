import re
import unicodedata
from typing import Union
from .utils import is_domain_valid, is_disposable
from .schemas import EmailResponse
from .exceptions_types import EmailFormatError, DisposableEmailError, EmailMXRecordError


class EmailValidator:
    def __init__(self, email: Union[str, bytes], **options):
        """
        Initialize the EmailValidator with an email address and optional settings.

        Args:
            email (Union[str, bytes]): The email address to validate. It can be a
                string or a bytes object. If bytes, it will be decoded to ASCII.
            **options: Optional keyword arguments to customize validation behavior.
                Default options include:
                - allow_smtputf8 (bool): Allow SMTPUTF8 in email validation.
                - allow_empty_local (bool): Allow emails with an empty local part.
                - allow_quoted_local (bool): Allow quoted local parts in the email.
                - allow_domain_literal (bool): Allow domain literals in the email.
                - allow_display_name (bool): Allow display names in the email.
                - check_deliverability (bool): Check if the email can be delivered.
                - test_environment (bool): Enable test environment settings.
                - globally_deliverable (bool): Check for global deliverability.
                - timeout (int): Timeout for validation operations in seconds.

        Raises:
            EmailFormatError: If the email is bytes and cannot be decoded to ASCII.
        """
        if isinstance(email, bytes):
            try:
                email = email.decode("ascii")
            except ValueError as e:
                raise EmailFormatError("The email address is not valid ASCII.") from e

        self.email = email
        self.options = {
            "allow_smtputf8": False,
            "allow_empty_local": False,
            "allow_quoted_local": False,
            "allow_domain_literal": False,
            "allow_display_name": False,
            "check_deliverability": True,
            "test_environment": False,
            "globally_deliverable": True,
            "timeout": 10,
            **options,
        }
        self.local_part, self.domain, self.display_name, self.is_quoted_local = (
            self._split_email()
        )

    def _split_email(self):
        """Split the email into display name, local part, and domain, handling quoted local parts."""
        match = re.match(r'(?:\"?([^@"]+)\"?\s)?<(.+)>|(.+)', self.email)
        if not match:
            raise EmailFormatError("Invalid email format.")

        display_name, addr_spec, fallback = match.groups()
        local_part, domain = (addr_spec or fallback).split("@", 1)

        # Handle quoted local part if allowed
        is_quoted_local = local_part.startswith('"') and local_part.endswith('"')
        if is_quoted_local and not self.options["allow_quoted_local"]:
            raise EmailFormatError("Quoted local part is not allowed.")

        local_part = unicodedata.normalize("NFC", local_part.strip('"'))
        domain = unicodedata.normalize("NFC", domain)

        return local_part, domain, display_name, is_quoted_local

    @staticmethod
    def _check_email_pattern(email: str) -> bool:
        """Check if the email matches the correct pattern using regex."""
        return bool(
            re.match(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$", email.strip())
        )

    def validate(self) -> EmailResponse:
        """Main validation entry point."""

        # Disposable email check
        if is_disposable(self.domain):
            raise DisposableEmailError("Disposable email addresses are not allowed.")

        if not self._check_email_pattern(self.email):
            raise EmailFormatError("Invalid email format.")

        # Domain literal check
        if self.domain.startswith("[") and self.domain.endswith("]"):
            if not self.options["allow_domain_literal"]:
                raise EmailFormatError("Domain literal is not allowed.")

        # MX Record check if deliverability checks are enabled
        if (
            self.options["check_deliverability"]
            and not self.options["test_environment"]
        ):
            if not is_domain_valid(self.domain):
                raise EmailMXRecordError("Domain has no valid MX records.")

        # Return validated email
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

    def is_globally_deliverable(self) -> bool:
        """Determine if the domain is globally deliverable, considering restricted TLDs."""

        # Check if global deliverability checks are enabled
        if not self.options.get("globally_deliverable", False):
            return True  # Skip check if not required

        # List of restricted or private TLDs that are generally non-global
        restricted_tlds = {"local", "example", "invalid", "test"}

        # Check the TLD of the domain
        tld = self.domain.split(".")[-1].lower()
        if tld in restricted_tlds:
            return False

        return is_domain_valid(self.domain)
