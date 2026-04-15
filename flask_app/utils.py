import random
import string
from datetime import datetime, date


def get_pergola_count():
    base_count = 10
    start_date = date(2026, 1, 1)
    today = date.today()
    if today < start_date:
        weeks = 0
    else:
        weeks = (today - start_date).days // 7
    return base_count + weeks


def generate_kp_number(pergola_type="B500"):
    short_type = pergola_type.replace("NEW", "")
    date_str = datetime.now().strftime("%d%m%y")
    rand_part = ''.join(random.choices(string.digits, k=4))
    return f"{short_type}-{date_str}-{rand_part}"
