from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

async def generate_hash(pw_raw):
    ph=PasswordHasher()
    return ph.hash(pw_raw)

async def verify_hash(self,pw_hash,pw_raw):
    ph=PasswordHasher()
    verified=False
    msg=""
    try:
        verified=ph.verify(pw_hash,pw_raw)
    except VerifyMismatchError:
        verified=False
        msg="Invalid password."
    except Exception as e:
        verified=False
        msg=f"Unexpected error: \n{e}"
    return verified,msg