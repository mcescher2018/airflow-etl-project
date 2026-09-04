from datetime import datetime

def get_today_str():
    today_str = datetime.now().strftime("%Y-%m-%d")
    return today_str