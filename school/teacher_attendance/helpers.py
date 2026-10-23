from datetime import timedelta


def attendance_dict(rec):
    """Real DB record → dict."""
    return {
        "id": rec.id,
        "date": rec.date.strftime("%Y-%m-%d"),
        "day_name": rec.date.strftime("%A"),
        "month": rec.date.strftime("%B"),
        "year": rec.date.year,
        "check_in_time": rec.check_in_time.strftime("%I:%M %p") if rec.check_in_time else None,
        "check_out_time": rec.check_out_time.strftime("%I:%M %p") if rec.check_out_time else None,
        "status": rec.status,           # present / absent / leave
        "working_hours": rec.working_hours,
        "remarks": rec.remarks,
        "is_virtual": False,
    }


def virtual_dict(date_obj, status_value):
    """
    DB me nahi hai — sirf response ke liye.
    status_value = 'absent' ya 'leave'
    """
    return {
        "id": None,
        "date": date_obj.strftime("%Y-%m-%d"),
        "day_name": date_obj.strftime("%A"),
        "month": date_obj.strftime("%B"),
        "year": date_obj.year,
        "check_in_time": None,
        "check_out_time": None,
        "status": status_value,         # 'absent' (ya 'leave' if virtual leave)
        "working_hours": 0.0,
        "remarks": "auto",
        "is_virtual": True,
    }


def fill_missing_dates(records, start_date, end_date, week_off_day=6):
    """
    records: list of dicts (already serialized). Each must have 'date' key (YYYY-MM-DD).
    start_date / end_date: datetime.date
    week_off_day: 0=Mon ... 6=Sun (default Sunday)
    Returns: list sorted by date DESC (newest first)
    """
    existing_dates = {rec['date'] for rec in records}
    filled = list(records)
    cursor = start_date

    while cursor <= end_date:
        date_str = cursor.strftime("%Y-%m-%d")
        if date_str not in existing_dates:
            is_week_off = (cursor.weekday() == week_off_day)
            # Week-off bhi 'absent' hi treat karte hain (choices me sirf 3 hi hain)
            status_value = 'absent'
            filled.append(virtual_dict(cursor, status_value))
        cursor += timedelta(days=1)

    filled.sort(key=lambda r: r['date'], reverse=True)
    return filled