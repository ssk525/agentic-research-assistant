from datetime import datetime, timezone

from sqlalchemy import Column, Integer, String, DateTime, create_engine
from sqlalchemy.orm import declarative_base

from src.config import settings

Base = declarative_base()


def _utcnow():
	return datetime.now(timezone.utc)


class Fact(Base):
	__tablename__ = "facts"
	id = Column(Integer, primary_key=True)
	entity = Column(String, index=True)
	attribute = Column(String)
	value = Column(String)
	source = Column(String)
	updated_at = Column(DateTime, default=_utcnow)


engine = create_engine(settings.database_url)


def init_db():
	Base.metadata.create_all(engine)
