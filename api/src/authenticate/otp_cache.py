import random
import string
import os
from src.cache.cache import cache

MASTER_OTP = os.environ.get('MASTER_OTP', '1408199')

def generate_otp(length: int = 6) -> str:
    """
    Generate numeric OTP of given length (default: 6).
    """
    return ''.join(random.choices(string.digits, k=length))


async def set_otp(user_id: str, ttl: int = 600) -> str:
    """
    Generate OTP, store in cache, and return it.
    Key is tied to user_id.
    """
    otp = generate_otp()
    await cache.set(f"otp:{user_id}", otp, ttl=ttl)
    return otp


def is_master_otp(otp: str) -> bool:
    """
    Check if the provided OTP is the master OTP.
    Returns True if OTP matches MASTER_OTP, False otherwise.
    """
    return otp == MASTER_OTP


async def verify_otp(user_id: str, otp: str, delete_after_verify: bool = True) -> bool:
    stored_otp = await cache.get(f"otp:{user_id}")

    # 1. Master OTP check
    if is_master_otp(otp):
        return True

    # 2. Normal OTP check
    if stored_otp and stored_otp == otp:
        if delete_after_verify:
            await cache.delete(f"otp:{user_id}")
        return True

    return False


async def verify_otp_keep(user_id: str, otp: str, delete_after_verify: bool = True) -> bool:
    """
    Verify OTP for given user_id.
    Returns True if valid, False otherwise.
    """
    stored = await cache.get(f"otp:{user_id}")
    if not stored or stored != otp:
        return False

    return True


async def delete_otp(user_id: str, otp: str) -> bool:
    """
    Verify OTP for given user_id.
    Returns True if valid, False otherwise.
    """
    await cache.delete(f"otp:{user_id}")
    return True