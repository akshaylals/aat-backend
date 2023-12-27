from sqlalchemy.orm import Session
from passlib.hash import bcrypt

from . import models, schemas


def get_user(db: Session, username: str):
    db_user = db.query(models.User).filter(models.User.username == username).first()
    if db_user:
        return schemas.UserAuth(**db_user.dict())
    else:
        return False

def create_user(db: Session, user: schemas.UserCreate):
    user.hashed_password = bcrypt.hash(user.hashed_password)
    db_user = models.User(**user.dict())
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_files(db: Session):
    return db.query(models.File).all()

def get_file(db: Session, file_id):
    return db.query(models.File).filter(models.File.id == file_id).first()

def create_file(db: Session, file: schemas.FileCreate):
    db_file = models.File(**file.dict())
    db.add(db_file)
    db.commit()
    db.refresh(db_file)
    return db_file

def get_annotations(db: Session, file_id):
    return db.query(models.Annotation).filter(models.Annotation.file_id == file_id).all()

def create_annotation(db: Session, annotation: schemas.AnnotationCreate):
    db_annotation = models.Annotation(**annotation.dict())
    db.add(db_annotation)
    db.commit()
    db.refresh(db_annotation)
    return db_annotation

def delete_annotation(db: Session, annotation_id: int):
    db_annotation = db.query(models.Annotation).filter(models.Annotation.id == annotation_id).first()
    if db_annotation:
        db.delete(db_annotation)
        db.commit()
        return db_annotation
    else:
        return None
