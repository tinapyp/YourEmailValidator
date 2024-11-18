from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from fastapi.responses import JSONResponse
from app.database import get_db
from app.auth.models import User, UserStatus
from app.core.utils import send_email
from app.auth.utils import generate_random_password, get_password_hash

import os
from dotenv import load_dotenv

load_dotenv()

router = APIRouter(prefix="/webhooks")

WEBHOOK_TOKEN = os.environ.get("WEBHOOK_TOKEN")


@router.post("/socialbuzz", name="socialbuzz")
async def socialbuzz(request: Request, db: Session = Depends(get_db)):
    """
    Webhook endpoint to upgrade a user to Donatur status.
    Validates the webhook token and updates the user's status.
    """
    # Validate webhook token
    token = request.headers.get("sb-webhook-token")
    if token != WEBHOOK_TOKEN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid webhook token",
        )

    try:
        # Parse the payload
        payload = await request.json()
        donatur_name = payload.get("supporter")
        donatur_email = payload.get("email_supporter")

        if not donatur_email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email not provided",
            )

        # Find the user by email
        user = db.query(User).filter(User.email == donatur_email).first()
        if not user:
            password = generate_random_password()
            hash_password = get_password_hash(password)
            user = User(
                username=donatur_name,
                email=donatur_email,
                password=hash_password,
                status=UserStatus.DONATUR,
            )
            db.add(user)
            db.commit()

            # Send email with user credentials
            try:
                send_email(
                    to_email=user.email,
                    subject="Welcome to Donatur Plan",
                    body=f"""Dear {user.email},

We are pleased to inform you that your account has been successfully created. Below are your login credentials:

- **Email:** {user.email}
- **Password:** {password}

For your security, we recommend that you log in as soon as possible and change your password to something more personal and secure.

If you have any questions or need assistance, please feel free to me at fathin@youremailvalidator.com.

Welcome aboard, and thank you for joining the Donatur Plan!

Best regards, 
Fathin
Maker of Your Email Validator
""",
                )
            except Exception as e:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Failed to send email: {str(e)}",
                )

        # Update the user's status to Donatur
        user.status = UserStatus.DONATUR
        db.commit()

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "message": f"User {user.email} successfully upgraded to Donatur",
            },
        )
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unexpected error: {str(e)}",
        )
