from sqlalchemy import Column, Integer, String, Date, Text, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql.schema import ForeignKey
from sqlalchemy.orm import relationship

Base = declarative_base()
 
class User(Base):
    __tablename__ = 'users'
    ...
    
    
class Post(Base):
    # Photo
    __tablename__ = "posts"
    ...
    
class Comment(Base):
    __tablename__ = 'comments'
    ...