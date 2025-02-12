import pytest
from fastapi import Depends

from sqlmodel import select

from app import db
from app.db import get_session
from app.models.users_model import User

@pytest.fixture(scope='module')
def setup():
    session = db.get_session()
    yield session
    #q=select(User).filter(email="sanjay@gmail.com")
    q=select(User).where(User.email == "sanjay@gmail.com")
    result=session.execute(q)
    user=result.first()
    if user:
        session.delete(user)
    # session.shutdown()
    session.commit()

def test_create_user(setup):
    User.create_user(email="sanjay@gmail.com",password="#sanjay@1234",session=Depends(get_session))

def test_duplicate_user(setup):
    with pytest.raises(Exception):
        User.create_user(email="sanjay@gmail.com",password="#sanjay@12345")

def test_invalid_email(setup):
    with pytest.raises(Exception):
        User.create_user(email="sanjay", password="#sanjay@12345")

def test_valid_password(setup):
    # with get_session() as session:
        session = db.get_session()
        yield session
        query=select(User).where(User.email=="sanjay@gmail.com")
        result= session.execute(query)

        user_object=result.first()
        assert user_object is not None
        assert user_object.verify_password('sanjay@1234')==True
        assert user_object.verify_password('sanjay@12345')==False