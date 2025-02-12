from fastapi import HTTPException
from pydantic import BaseModel, EmailStr, SecretStr, validator, root_validator


class UserLogin(BaseModel):
    email:EmailStr
    password:SecretStr
    session_id:str=None

    @root_validator(pre=True)
    def validate_user(cls, values):
        err_msg = "Incorrect Credentials, Please Try again"
        email = values.get("email")
        password = values.get("password")
        if email is None or password is None:
            # raise ValueError("")
            raise HTTPException(status_code=400, detail=err_msg)

        return values

class UserSignup(BaseModel):
    email:EmailStr
    password:SecretStr
    confirm_password:SecretStr

    @validator("confirm_password")
    def password_match(cls, v,values,**kwargs):
        password=values.get('password')
        #confirm_password=v
        if password!=v:
            # raise ValueError("Passwords do not match")
            raise HTTPException(status_code=400, detail="Passwords do not match")
        return v


# @validator("email")
    # def email_available(cls,v,values,**kwargs):
    #     #query=select(User).filter(email=v)
    #     query = select(User).where(User.email == v)
    #     # if query:
    #     #     raise ValueError("Email is not available")
    #     # return v
    #     session=values.get("session")
    #     result=session.execute(query)
    #     user=result.all()
    #     if user:
    #         raise ValueError("Email is not available")
    #     return v