from sqlalchemy import Column, ForeignKey, Integer, String, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine
from werkzeug.security import generate_password_hash
from werkzeug.security import check_password_hash
import datetime

Base = declarative_base()

class Users(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username =Column(String(50), unique=True)
    email= Column(String(40), unique=True)
    password =Column(String(66))
    created_date=Column(DateTime, default= datetime.datetime.now)

    def __init__(self, username, password, email):
        self.username= username
        self.password=self.__create_password(password)
        self.email=email

    def __create_password(self, password):
        return generate_password_hash(password)

    def verify_password(self, password):
        print self.password, password
        return check_password_hash(self.password, password)


class Catalogs(Base):
    __tablename__ = 'catalogs'
    id = Column(Integer, primary_key=True)
    namecat = Column(String(50))

    def __init__(self, namecat):
        self.namecat= namecat
    
    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'namecat': self.namecat,
            'id': self.id
        }

class Items(Base):
    __tablename__ = 'items'
    id = Column(Integer, primary_key=True)
    name =Column(String(50), unique=True)
    description=Column(Text(250))
    catalog_id=Column(Integer, ForeignKey('catalogs.id'))
    catalog = relationship(Catalogs)

    def __init__(self, name, description, catalog_id):
        self.name= name
        self.description= description
        self.catalog_id=catalog_id
    
    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'name': self.name,
            'description':self.description,
            'id': self.id
        }

engine = create_engine('sqlite:///database.db')


Base.metadata.create_all(engine)

