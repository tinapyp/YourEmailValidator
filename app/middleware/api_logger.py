from fastapi import Request
from datetime import datetime
from ..database import get_db
from ..models.models import APIKey, APIUsage


async def log_api_requests(request: Request, call_next):
    """
    Middleware to log API requests and track usage
    """
    if request.url.path.startswith("/api/"):
        start_time = datetime.now()
        api_key = request.headers.get("X-API-Key")

        response = await call_next(request)

        if api_key:
            db = next(get_db())
            key_record = (
                db.query(APIKey)
                .filter(APIKey.key == api_key, APIKey.is_active == True)
                .first()
            )

            if key_record:
                end_time = datetime.now()
                response_time = (end_time - start_time).total_seconds() * 1000

                usage_log = APIUsage(
                    user_id=key_record.user_id,
                    api_key_id=key_record.id,
                    endpoint=request.url.path,
                    is_success=response.status_code < 400,
                    response_time=response_time,
                )

                key_record.usage_count += 1
                db.add(usage_log)
                db.commit()

        return response
    return await call_next(request)
