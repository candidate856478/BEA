from sqlalchemy import (
    Column,
    Index,
    Integer,
    Text,
    String,
    CHAR,
    Float,
    Date,
    ForeignKey,
)
from sqlalchemy.orm import relationship
from time import strptime
from .meta import Base

class AccountType(Base):
    __tablename__ = 'account_type'
    id = Column(Integer, primary_key=True)
    label = Column(String(60), nullable=False)

class Account(Base):
    __tablename__ = 'account'
    id = Column(Integer, primary_key=True)
    number = Column(String(16))
    balance = Column(Float)
    account_type_id = Column(
        Integer,
        ForeignKey('account_type.id'),
        nullable=False,
        )
    accountType = relationship('AccountType', backref='accounts')

class Client(Base):
    __tablename__ = 'client'
    id = Column(Integer, primary_key=True)
    login = Column(String(16), nullable=False)
    password = Column(String(64), nullable=False)
    name = Column(String(60), nullable=False)
    first_name = Column(String(60), nullable=False)
    birth_date = Column(Date, nullable=False)
    address = Column(String(80), nullable=False)
    lat = Column(Float)
    lng = Column(Float)

class AccountClient(Base):
    __tablename__ = 'account_client'
    client_id = Column(
        Integer, 
        ForeignKey('client.id'),
        primary_key=True,
        )
    account_id = Column(
        Integer,
        ForeignKey('account.id'),
        primary_key=True,
        )
    client = relationship('Client', backref='clients')
    account = relationship('Account', backref='accounts')

def clientValidation(client):
    """ Client attributes validation
    """
    msg = ''

    if len(client.login) == 0:
        msg = 'Login is mandatory.'
    elif len(client.password) == 0:
        msg = 'Password is mandatory.'
    elif len(client.name) == 0:
        msg = 'Name is mandatory.'
    elif len(client.first_name) == 0:
        msg = 'First name is mandatory.'
    elif len(client.birth_date) == 0:
        msg = 'Birth date is mandatory.'
    elif len(client.address) == 0:
        msg = 'Address is mandatory.'

    if len(msg) == 0:
        try:
            strptime(client.birth_date, "%Y-%m-%d")
        except ValueError:
            msg = 'Wrong date format.'

    return msg