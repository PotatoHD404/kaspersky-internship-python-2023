from sqlalchemy import Column, String, Boolean, UUID, ARRAY

from database import Base


class Search(Base):
    __tablename__ = "searches"

    id = Column(UUID, primary_key=True, index=True)
    finished = Column(Boolean)
    paths = Column(String)
