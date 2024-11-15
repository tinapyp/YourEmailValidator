from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List, Tuple

from app.api.utils import verify_api_key_header, verify_donatur_access
from app.auth.models import User, UserStatus
from .schemas import SingleEmailRequest, BulkEmailRequest, EmailResponse
from .email_validator import (
    EmailValidator,
    EmailFormatError,
    DisposableEmailError,
    EmailMXRecordError,
)
from app.api.models import APIKey

router = APIRouter(prefix="/api/v1")


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


@router.post("/bulk-email-validate", response_model=List[EmailResponse])
async def bulk_validate_email(
    request: BulkEmailRequest,
    auth: Tuple[APIKey, Session] = Depends(
        verify_donatur_access
    ),  # Use the new dependency
):
    """Endpoint to validate a list of emails. Only available for DONATUR users."""
    api_key, db = auth

    # Optional: Add limit to number of emails in a single request
    MAX_BULK_EMAILS = 1000  # You can adjust this number
    if len(request.email) > MAX_BULK_EMAILS:
        raise HTTPException(
            status_code=400,
            detail=f"Maximum {MAX_BULK_EMAILS} emails allowed per request",
        )

    responses = []
    success_count = 0

    for email in request.email:
        email_validator = EmailValidator(email)
        try:
            # Perform email validation
            email_validator.validate()
            response = EmailResponse(
                email=email, is_valid=True, message="Email is valid."
            )
            success_count += 1
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

    # Log usage for bulk validation
    try:
        # Log each email validation as a separate usage
        for _ in range(len(request.email)):
            usage_log = APIUsage(
                user_id=api_key.user_id,
                api_key_id=api_key.id,
                endpoint="/api/v1/bulk-validate",
                is_success=True,
                response_time=0,  # You could add actual timing if needed
            )
            db.add(usage_log)

        api_key.usage_count += len(request.email)
        db.commit()
    except Exception as e:
        db.rollback()
        # Log the error but don't fail the request since validation was successful
        print(f"Error logging API usage: {str(e)}")

    return responses


@router.get("/check-bulk-access")
async def check_bulk_validation_access(
    auth: Tuple[APIKey, Session] = Depends(verify_api_key_header),
):
    """Check if the current user has access to bulk validation."""
    api_key, db = auth
    user = db.query(User).filter(User.id == api_key.user_id).first()

    return {
        "has_access": user.status == UserStatus.DONATUR,
        "current_status": user.status,
        "required_status": UserStatus.DONATUR,
        "upgrade_required": user.status != UserStatus.DONATUR,
    }
