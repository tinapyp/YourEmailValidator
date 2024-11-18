from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from fastapi.responses import JSONResponse
from app.database import get_db
from app.auth.models import User, UserStatus
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
        email_donatur = payload.get("email_supporter")

        if not email_donatur:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email not provided",
            )

        # Find the user by email
        user = db.query(User).filter(User.email == email_donatur).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with email {email_donatur} not found",
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
