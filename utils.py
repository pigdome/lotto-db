from datetime import datetime, timedelta
import pytz

def get_thai_tz():
    return pytz.timezone('Asia/Bangkok')

def next_thai_lottery(now: datetime):
    # Thai lottery is on 1st and 16th
    # results usually out around 14:00-16:00
    # we'll use 12:00 as requested by the user
    
    cutoff_hour = 12
    
    # Try current month first
    for day in [1, 16]:
        candidate = now.replace(day=day, hour=cutoff_hour, minute=0, second=0, microsecond=0)
        if candidate > now:
            return candidate
            
    # Try next month
    if now.month == 12:
        candidate = now.replace(year=now.year + 1, month=1, day=1, hour=cutoff_hour, minute=0, second=0, microsecond=0)
    else:
        candidate = now.replace(month=now.month + 1, day=1, hour=cutoff_hour, minute=0, second=0, microsecond=0)
    return candidate

def next_weekly_lottery(now: datetime, target_days: list, target_hour: int, target_minute: int):
    # target_days as list of ints (0=Mon, 6=Sun)
    # results are at target_hour:target_minute
    
    current_day = now.weekday()
    
    # Check for today or future days in the same week
    for day in sorted(target_days):
        if day > current_day:
            return (now + timedelta(days=day - current_day)).replace(hour=target_hour, minute=target_minute, second=0, microsecond=0)
        elif day == current_day:
            candidate = now.replace(hour=target_hour, minute=target_minute, second=0, microsecond=0)
            if candidate > now:
                return candidate
                
    # Next week
    next_day = sorted(target_days)[0]
    days_to_add = (7 - current_day) + next_day
    return (now + timedelta(days=days_to_add)).replace(hour=target_hour, minute=target_minute, second=0, microsecond=0)

def next_daily_lottery(now: datetime, target_hour: int, target_minute: int):
    candidate = now.replace(hour=target_hour, minute=target_minute, second=0, microsecond=0)
    if candidate > now:
        return candidate
    return candidate + timedelta(days=1)

def get_all_next_draws(threshold_mins: int = 1440):
    tz = get_thai_tz()
    now = datetime.now(tz)
    
    # Check if we should use 5-day schedule for Lao Development (starts April 2, 2026)
    lao_dev_days = [0, 2, 4] # Current: Mon, Wed, Fri
    if now.year >= 2026 and (now.month > 4 or (now.month == 4 and now.day >= 2)):
        lao_dev_days = [0, 1, 2, 3, 4] # Mon-Fri
        
    results = [
        {
            "id": "thai",
            "name": "หวยไทย",
            "next_draw": next_thai_lottery(now).isoformat(),
            "bg": "bg-[#4338ca]" # Indigo
        },
        {
            "id": "lao",
            "name": "หวยลาวพัฒนา",
            "next_draw": next_weekly_lottery(now, lao_dev_days, 20, 30).isoformat(),
            "bg": "bg-[#0ea5e9]" # Sky
        },
        {
            "id": "lao_star",
            "name": "หวยลาวสตาร์",
            "next_draw": next_daily_lottery(now, 15, 45).isoformat(),
            "bg": "bg-[#06b6d4]" # Cyan
        },
        {
            "id": "lao_vip",
            "name": "หวยลาว VIP",
            "next_draw": next_daily_lottery(now, 20, 00).isoformat(),
            "bg": "bg-[#3b82f6]" # Blue
        },
        {
            "id": "hanoi_special",
            "name": "หวยฮานอยพิเศษ",
            "next_draw": next_daily_lottery(now, 17, 30).isoformat(),
            "bg": "bg-[#f59e0b]" # Amber
        },
        {
            "id": "hanoi",
            "name": "หวยฮานอย",
            "next_draw": next_daily_lottery(now, 18, 30).isoformat(),
            "bg": "bg-[#ef4444]" # Red
        },
        {
            "id": "hanoi_vip",
            "name": "หวยฮานอย VIP",
            "next_draw": next_daily_lottery(now, 19, 30).isoformat(),
            "bg": "bg-[#dc2626]" # Dark Red
        }
    ]
    
    # Filter only those within threshold
    filtered = []
    for r in results:
        target = datetime.fromisoformat(r["next_draw"])
        diff_mins = (target - now).total_seconds() / 60
        if diff_mins <= threshold_mins:
            filtered.append(r)
            
    return filtered

if __name__ == "__main__":
    import json
    print(json.dumps(get_all_next_draws(), indent=2))
