from fastapi import APIRouter, HTTPException, Depends, Header
from sqlalchemy.orm import Session
from typing import List, Optional, Tuple
from .schemas import SingleEmailRequest, BulkEmailRequest, EmailResponse
from .email_validator import (
    EmailValidator,
    EmailFormatError,
    DisposableEmailError,
    EmailMXRecordError,
)
from app.database import get_db
from app.auth.dependencies import verify_api_key
from app.api.models import APIKey, APIUsage
from app.core.utils import check_user_limit
from datetime import datetime

router = APIRouter(prefix="/api/v1")


async def verify_api_key_header(
    x_api_key: str = Header(...), db: Session = Depends(get_db)
) -> tuple[APIKey, Session]:
    """Verify API key and return the associated user and API key record."""
    user = verify_api_key(x_api_key, db)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid API key")

    # Get API key record
    api_key = (
        db.query(APIKey)
        .filter(APIKey.key == x_api_key, APIKey.is_active == True)
        .first()
    )

    # Check usage limits
    if not check_user_limit(user.id, db):
        raise HTTPException(
            status_code=429,
            detail="Monthly API limit reached. Please upgrade to Donatur status for unlimited access.",
        )

    return api_key, db


@router.post("/validate-email", response_model=EmailResponse)
async def validate_email(
    request: SingleEmailRequest,
    auth: tuple[APIKey, Session] = Depends(verify_api_key_header),
):
    """Endpoint to validate a single email."""
    api_key, db = auth
    email_validator = EmailValidator(request.email)
    try:
        # Perform email validation
        email_validator.validate()
        return EmailResponse(
            email=request.email, is_valid=True, message="Email is valid."
        )
    except (EmailFormatError, DisposableEmailError, EmailMXRecordError) as e:
        # Return specific error message
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/check-disposable", response_model=EmailResponse)
async def check_disposable_email(
    request: SingleEmailRequest,
    auth: tuple[APIKey, Session] = Depends(verify_api_key_header),
):
    """Endpoint to check if an email is disposable."""
    api_key, db = auth
    email_validator = EmailValidator(request.email)
    try:
        # Check if email is disposable
        email_validator.check_disposable()
        return EmailResponse(
            email=request.email, is_valid=True, message="Email is not disposable."
        )
    except Exception as e:
        # Return specific error message
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/check-mx-record", response_model=EmailResponse)
async def check_mx_record_email(
    request: SingleEmailRequest,
    auth: tuple[APIKey, Session] = Depends(verify_api_key_header),
):
    """Endpoint to check if an email has valid MX records."""
    api_key, db = auth
    email_validator = EmailValidator(request.email)
    try:
        # Check if email has valid MX record
        email_validator.check_mx_record()
        return EmailResponse(
            email=request.email, is_valid=True, message="Email has valid MX records."
        )
    except Exception as e:
        # Return specific error message
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/bulk-validate", response_model=List[EmailResponse])
async def bulk_validate_email(
    request: BulkEmailRequest,
    auth: Tuple[str, str] = Depends(verify_api_key_header),
):
    """Endpoint to validate a list of emails."""
    api_key, db = auth

    # Count this as multiple API calls based on number of emails
    total_emails = len(request.email)

    responses = []

    for email in request.email:
        email_validator = EmailValidator(email)
        try:
            # Perform email validation
            email_validator.validate()
            response = EmailResponse(
                email=email, is_valid=True, message="Email is valid."
            )
        except EmailFormatError:
            response = EmailResponse(
                email=email, is_valid=False, message="Invalid email format."
            )
        except DisposableEmailError:
            response = EmailResponse(
                email=email,
                is_valid=False,
                message="Disposable email addresses are not allowed.",
            )
        except EmailMXRecordError:
            response = EmailResponse(
                email=email, is_valid=False, message="Domain has no valid MX records."
            )

        responses.append(response)

    return responses
