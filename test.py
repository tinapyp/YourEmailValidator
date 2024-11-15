import pytest
from app.services.email_validator import EmailValidator
from app.services.email_validator import (
    EmailFormatError,
    DisposableEmailError,
    EmailMXRecordError,
)
from app.services.email_validator import EmailResponse


@pytest.mark.parametrize(
    "email, expected_valid",
    [
        ("test@example.com", True),
        ("fathin+waiting@yahoo.co.id", True),
        ("user@sub.domain.com", True),
        ("@invalid-email.com", False),
        ("@missinglocalpart.com", False),
        ("@missingatsign.com", False),
    ],
)
def test_validate_email_format(email, expected_valid):
    if expected_valid:
        response = EmailValidator(email).validate()
        assert isinstance(response, EmailResponse)
        assert response.is_valid
    else:
        with pytest.raises(EmailFormatError):
            EmailValidator(email).validate()


@pytest.mark.parametrize(
    "email, allow_quoted_local, expected_valid",
    [
        ('"quoted"@example.com', True, True),  # Allow quoted local part
        ('"quoted"@example.com', False, False),  # Disallow quoted local part
    ],
)
def test_allow_quoted_local(email, allow_quoted_local, expected_valid):
    # Setup options dictionary with the given allow_quoted_local flag
    options = {"allow_quoted_local": allow_quoted_local}

    # Initialize EmailValidator with the provided email and options
    validator = EmailValidator(email, **options)

    if expected_valid:
        # If we expect it to be valid, validate and check if response is valid
        response = validator.validate()
        assert isinstance(response, EmailResponse)
        assert (
            response.is_valid
        )  # The email should be valid if quoted local part is allowed
    else:
        # If we expect an error, validate should raise an EmailFormatError
        with pytest.raises(EmailFormatError, match="Quoted local part is not allowed."):
            validator.validate()


@pytest.mark.parametrize(
    "email, is_disposable",
    [
        ("test@mailinator.com", True),
        ("test@gmail.com", False),
    ],
)
def test_disposable_email_check(email, is_disposable):
    validator = EmailValidator(email)
    response = validator.check_disposable()
    assert response.is_valid != is_disposable
    if is_disposable:
        assert "disposable" in response.message
    else:
        assert "not disposable" in response.message


@pytest.mark.parametrize(
    "email, has_mx",
    [
        ("test@gmail.com", True),
        ("test@invalid-domain.xyz", False),
    ],
)
def test_mx_record_check(email, has_mx):
    validator = EmailValidator(email)
    if has_mx:
        response = validator.check_mx_record()
        assert response.is_valid
        assert "Valid MX records found" in response.message
    else:
        with pytest.raises(EmailMXRecordError):
            validator.validate()


@pytest.mark.parametrize(
    "email, globally_deliverable",
    [
        ("test@example.com", True),
        ("test@local", False),
        ("test@invalid", False),
    ],
)
def test_globally_deliverable_check(email, globally_deliverable):
    validator = EmailValidator(email, globally_deliverable=True)
    if globally_deliverable:
        assert validator.is_globally_deliverable() is True
    else:
        assert validator.is_globally_deliverable() is False
