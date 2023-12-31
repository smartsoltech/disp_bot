from sqlalchemy import create_engine, Column, Integer, String, Boolean, ForeignKey, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from icecream import ic
import enum

DATABASE_URL = "sqlite:///db/test.db"
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)
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

class IssueStatus(enum.Enum):
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
    phone = Column(String)  # Добавлено поле для телефона
    status = Column(Enum(IssueStatus), default=IssueStatus.NEW.name)
    issuer_id = Column(Integer, ForeignKey('issuers.id'))
    issuer = relationship('Issuer')

Base.metadata.create_all(engine)

def get_user_language(telegram_id):
    session = Session()
    user = session.query(User).filter_by(telegram_id=telegram_id).first()
    session.close()
    return user.language if user else 'en'

def get_issues_by_status(status):
    session = Session()
    issues = session.query(Issue).filter_by(status=status).all()
    session.close()
    return issues

def update_issue_status(issue_id, new_status):
    session = Session()
    issue = session.query(Issue).filter_by(id=issue_id).first()
    if issue:
        issue.status = new_status
        session.commit()
    session.close()

def get_user_language(telegram_id):
    session = Session()
    user = session.query(User).filter_by(telegram_id=telegram_id).first()
    session.close()
    return user.language if user else 'en'

def update_user_language(telegram_id, language):
    session = Session()
    user = session.query(User).filter_by(telegram_id=telegram_id).first()
    if user:
        user.language = language
        session.commit()
    session.close()

def save_new_issue(issue_data, chat_id):
    session = Session()
    # Находим или создаем нового заявителя
    issuer = session.query(Issuer).filter_by(telegram_id=chat_id).first()
    if not issuer:
        issuer = Issuer(telegram_id=chat_id)
        session.add(issuer)
        session.commit()

    # Создаем новую заявку
    new_issue = Issue(
        description=issue_data.get('description', ''),
        address=issue_data.get('address', ''),
        location=str(issue_data.get('location', '')),
        photo=issue_data.get('photo', ''),
        phone=issue_data.get('phone', ''),
        status=IssueStatus.NEW,
        issuer_id=issuer.id
    )
    session.add(new_issue)
    session.commit()
    session.close()

def get_all_issues():
    session = Session()
    issues = session.query(Issue).all()
    session.close()
    return issues
