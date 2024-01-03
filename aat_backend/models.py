from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, JSON
from sqlalchemy.orm import relationship

from .database import Base


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    full_name = Column(String, index=True)
    hashed_password = Column(String, index=True)

    projects = relationship("Project", back_populates="owner")

    def dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'full_name': self.full_name,
            'hashed_password': self.hashed_password,
        }


class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    path = Column(String, unique=True, index=True)

    owner_id = Column(Integer, ForeignKey("users.id"))
    owner = relationship("User", back_populates="projects")

    annotations = relationship("Annotation", back_populates="project")


class Annotation(Base):
    __tablename__ = "annotations"

    id = Column(Integer, primary_key=True, index=True)
    note = Column(String, index=True)
    coordinates = Column(JSON)
    project_id = Column(Integer, ForeignKey("projects.id"))

    project = relationship("Project", back_populates="annotations")

    def dict(self):
        return {
            'id': self.id,
            'note': self.note,
            'coordinates': self.coordinates,
        }
