import os
import asyncio
from fastapi import FastAPI, HTTPException, Depends, status, WebSocket, WebSocketDisconnect, UploadFile, File
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from . import crud, models, schemas
from .database import engine, get_db

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)


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
    file_path = os.path.join('data', file.path)
    if os.path.exists(file_path):
        return FileResponse(path=file_path, media_type='application/octet-stream', status_code=status.HTTP_200_OK)
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='File not found')

@app.post("/files")
def create_upload_file(file: UploadFile, db: Session = Depends(get_db)):
    try:
        contents = file.file.read()
        path = os.path.join('data', file.filename)
        with open(path, 'wb') as f:
            f.write(contents)
    except Exception:
        return {"message": "There was an error uploading the file"}
    finally:
        file.file.close()
    
    file_sch = schemas.FileCreate(path=file.filename)
    file_orm = crud.create_file(db, file_sch)
    return file_orm

@app.post("/annotations/", response_model=schemas.Annotation)
def create_annotations(annotation: schemas.AnnotationCreate, db: Session = Depends(get_db)):
    annotation = crud.create_annotation(db, annotation=annotation)
    return annotation

@app.delete("/annotations/{annotation_id}")
def delete_annotations(annotation_id: int, db: Session = Depends(get_db)):
    annotation = crud.delete_annotation(db, annotation_id)
    if annotation:
        return annotation
    else:
        raise HTTPException(status_code=404, detail="Annotation not found")

@app.websocket("/files/{file_id}/annotations")
async def websocket_endpoint(websocket: WebSocket, file_id: int, db: Session = Depends(get_db)):
    await websocket.accept()
    try:
        while True:
            annotations_orm = crud.get_annotations(db, file_id=file_id)
            annotations = [annotation.dict() for annotation in annotations_orm]
            await websocket.send_json(annotations)
            await asyncio.sleep(5)
    except WebSocketDisconnect:
        print("Websocket disconnected")