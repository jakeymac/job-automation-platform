from croniter import croniter
from datetime import datetime

def validate_job_schedule(schedule):
    """
    Validates that the given schedule is a valid cron expression.
    This is a very basic validation and can be improved with a proper cron parser.
    """
    try:
        croniter(schedule, datetime.now())
        return {"valid": True, "error": None}
    except Exception as e:
        return {"valid": False, "error": str(e)}
