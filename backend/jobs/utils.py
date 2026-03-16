def validate_cron_schedule(schedule):
    """
    Validates that the given schedule is a valid cron expression.
    This is a very basic validation and can be improved with a proper cron parser.
    """
    parts = schedule.split()
    if len(parts) != 5:
        return False
    for part in parts:
        if part != "*" and not part.isdigit():
            return False
    return True
