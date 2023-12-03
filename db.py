from sqlalchemy import create_engine, Column, Integer, String, Boolean, ForeignKey, engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.dialects.postgresql import ENUM as PENUM
import sqlalchemy
import openpyxl
import databases
import enum

DATABASE_URL = "sqlite+aiosqlite:///db/test.db"
database = databases.Database(DATABASE_URL)

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    admin = Column(Boolean)
    telegram_id = Column(String)

class Issuer(Base):
    __tablename__ = 'issuers'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    phone = Column(String)
    telegram_id = Column(String)

class IssueStatus(str, enum.Enum):
    NEW = "Новый"
    IN_PROGRESS = "В работе"
    RESOLVED = "Устранено"

class Issue(Base):
    __tablename__ = 'issues'
    id = Column(Integer, primary_key=True)
    description = Column(String)
    address = Column(String)
    location = Column(String)
    photo = Column(String)
    status = Column(PENUM(IssueStatus), default=IssueStatus.NEW.name)
    issuer_id = Column(Integer, ForeignKey('issuers.id'))
    issuer = relationship('Issuer')

# engine = sqlalchemy.create_engine(DATABASE_URL)
# Base.metadata.create_all(engine)

    
async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        
async def get_issues_by_status(status):
    query = sqlalchemy.select([Issue]).where(Issue.status == status)
    return await database.fetch_all(query)

async def update_issue_status(issue_id, new_status):
    query = sqlalchemy.update(Issue).where(Issue.id == issue_id).values(status=new_status)
    await database.execute(query)

async def is_user_admin(telegram_id):
    query = sqlalchemy.select([User]).where(User.telegram_id == str(telegram_id))
    user = await database.fetch_one(query)
    return user.admin if user else False
