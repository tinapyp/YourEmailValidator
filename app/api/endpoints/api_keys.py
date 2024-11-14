from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ...database import get_db
from ...dependencies import get_current_user_optional
from ...models.models import User, APIKey
from ...schemas.schemas import APIKeyCreate, APIKeyResponse

router = APIRouter()


@router.post("/keys", response_model=APIKeyResponse)
async def create_api_key(
    key_data: APIKeyCreate,
    current_user: User = Depends(get_current_user_optional),
    db: Session = Depends(get_db),
):
    new_key = APIKey(
        key=APIKey.generate_key(), name=key_data.name, user_id=current_user.id
    )
    db.add(new_key)
    db.commit()
    db.refresh(new_key)

    return APIKeyResponse(
        id=new_key.id,
        name=new_key.name,
        key=new_key.key,
        created_at=new_key.created_at,
        usage_count=new_key.usage_count,
    )


@router.delete("/keys/{key_id}")
async def delete_api_key(
    key_id: int,
    current_user: User = Depends(get_current_user_optional),
    db: Session = Depends(get_db),
):
    api_key = (
        db.query(APIKey)
        .filter(APIKey.id == key_id, APIKey.user_id == current_user.id)
        .first()
    )

    if not api_key:
        raise HTTPException(status_code=404, detail="API key not found")

    api_key.is_active = False
    db.commit()

    return {"message": "API key deleted successfully"}
