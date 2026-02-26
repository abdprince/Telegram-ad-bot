import random
import string
from typing import Optional

def generate_referral_code(telegram_id: int) -> str:
    """توليد كود إحالة فريد"""
    chars = string.ascii_uppercase + string.digits
    random_part = ''.join(random.choices(chars, k=6))
    return f"REF{telegram_id}{random_part}"

def format_balance(balance: float, coin_name: str = "جوهرة") -> str:
    """تنسيق عرض الرصيد"""
    return f"{balance:.2f} {coin_name}"

def calculate_ad_reward(user_stats: dict) -> float:
    """حساب المكافأة بناءً على إحصائيات المستخدم"""
    base_reward = 0.01
    # زيادة المكافأة للمستخدمين النشطين
    if user_stats.get('total_ads', 0) > 100:
        return base_reward * 2
    return base_reward
