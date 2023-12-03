import os

from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from . import crud, models, schemas
from .database import SessionLocal, engine

models.Base.metadata.create_all(bind=engine)

app = FastAPI()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/files", response_model=list[schemas.File])
def get_files(db: Session = Depends(get_db)):
    files = crud.get_files(db)
    return files

@app.get("/files/{file_id}/annotations/", response_model=list[schemas.Annotation])
def get_file_annotations(file_id: int, db: Session = Depends(get_db)):
    annotations = crud.get_annotations(db, file_id=file_id)
    return annotations

@app.get("/files/{file_id}/data", response_model=list[schemas.Annotation])
def get_file(file_id: int, db: Session = Depends(get_db)):
    file = crud.get_file(db, file_id=file_id)
    file_path = os.path.join('data', file.path, 'scene.gltf')
    if os.path.exists(file_path):
        return FileResponse(path=file_path, media_type='application/octet-stream', status_code=status.HTTP_200_OK)
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='File not found')

@app.post("/annotations/", response_model=schemas.Annotation)
def create_annotations(annotation: schemas.AnnotationCreate, db: Session = Depends(get_db)):
    annotation = crud.create_annotation(db, annotation=annotation)
    return annotation