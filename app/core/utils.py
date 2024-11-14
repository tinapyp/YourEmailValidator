from datetime import datetime, timedelta
from sqlalchemy import func
from sqlalchemy.orm import Session
from app.api.models import APIUsage
from app.auth.models import User, UserStatus
from typing import Dict, Any


def get_usage_stats(user_id: int, db: Session, days: int = 30) -> Dict[str, Any]:
    today = datetime.now().date()
    start_date = today - timedelta(days=days)

    daily_usage = (
        db.query(
            func.date(APIUsage.timestamp).label("date"),
            func.count(APIUsage.id).label("count"),
        )
        .filter(APIUsage.user_id == user_id, APIUsage.timestamp >= start_date)
        .group_by(func.date(APIUsage.timestamp))
        .all()
    )

    # Create a dict with all dates
    usage_dict = {(start_date + timedelta(days=i)): 0 for i in range(days + 1)}

    # Fill in actual usage
    for date, count in daily_usage:
        usage_dict[date] = count

    # Calculate success rate
    total_calls = db.query(APIUsage).filter(APIUsage.user_id == user_id).count()

    successful_calls = (
        db.query(APIUsage)
        .filter(APIUsage.user_id == user_id, APIUsage.is_success == True)
        .count()
    )

    success_rate = (successful_calls / total_calls * 100) if total_calls > 0 else 0

    return {
        "dates": list(usage_dict.keys()),
        "calls": list(usage_dict.values()),
        "total_calls": total_calls,
        "success_rate": success_rate,
    }


def check_user_limit(user_id: int, db: Session) -> bool:
    """
    Check if user has reached their monthly limit
    Returns True if user can make more requests, False otherwise
    """
    # Get the first day of current month
    today = datetime.now()
    start_of_month = today.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    # Get user status
    user = db.query(User).filter(User.id == user_id).first()

    # If user is DONATUR, they have no limit
    if user.status == UserStatus.DONATUR:
        return True

    # Count this month's usage
    monthly_usage = (
        db.query(func.count(APIUsage.id))
        .filter(APIUsage.user_id == user_id, APIUsage.timestamp >= start_of_month)
        .scalar()
    )

    # FREE users have 100 requests per month limit
    return monthly_usage < 100
