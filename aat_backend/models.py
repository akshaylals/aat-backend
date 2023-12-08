from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, JSON
from sqlalchemy.orm import relationship

from .database import Base


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
