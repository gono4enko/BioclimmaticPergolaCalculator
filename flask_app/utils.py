import random
import string
from datetime import datetime, date, timedelta


def get_pergola_count():
    current_week = datetime.now().isocalendar()[1]
    return max(1, current_week - 6)


def generate_kp_number(pergola_type="B500"):
    short_type = pergola_type.replace("NEW", "")
    date_str = datetime.now().strftime("%d%m%y")
    rand_part = ''.join(random.choices(string.digits, k=4))
    return f"{short_type}-{date_str}-{rand_part}"


def get_deadline_str(calc_date=None):
    if calc_date is None:
        calc_date = date.today()
    return (calc_date + timedelta(days=14)).strftime('%d.%m.%Y')
