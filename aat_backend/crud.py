from sqlalchemy.orm import Session

from . import models, schemas


def get_files(db: Session):
    return db.query(models.File).all()

def get_file(db: Session, file_id):
    return db.query(models.File).filter(models.File.id == file_id).first()

def get_annotations(db: Session, file_id):
    return db.query(models.Annotation).filter(models.Annotation.file_id == file_id).all()

def create_annotation(db: Session, annotation: schemas.AnnotationCreate):
    db_annotation = models.Annotation(**annotation.dict())
    db.add(db_annotation)
    db.commit()
    db.refresh(db_annotation)
    return db_annotation