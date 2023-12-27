from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, JSON
from sqlalchemy.orm import relationship

from .database import Base


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    full_name = Column(String, index=True)
    hashed_password = Column(String, index=True)

    def dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'full_name': self.full_name,
            'hashed_password': self.hashed_password,
        }


class File(Base):
    __tablename__ = "files"

    id = Column(Integer, primary_key=True, index=True)
    path = Column(String, unique=True, index=True)

    annotations = relationship("Annotation", back_populates="file")


class Annotation(Base):
    __tablename__ = "annotations"

    id = Column(Integer, primary_key=True, index=True)
    note = Column(String, index=True)
    coordinates = Column(JSON)
    file_id = Column(Integer, ForeignKey("files.id"))

    file = relationship("File", back_populates="annotations")

    def dict(self):
        return {
            'id': self.id,
            'note': self.note,
            'coordinates': self.coordinates,
        }
