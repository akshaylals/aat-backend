import os
from datetime import datetime, timedelta
from typing import Annotated

from fastapi import FastAPI, HTTPException, Depends, status, WebSocket, WebSocketDisconnect, UploadFile
from fastapi.responses import FileResponse, RedirectResponse
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from jose import JWTError, jwt
from passlib.context import CryptContext


from . import crud, models, schemas
from .database import engine, get_db
from .schemas import User, UserInDB, TokenData, Token


# to get a string like this run:
# openssl rand -hex 32
SECRET_KEY="48d56adc96ef62fd6d10a01ce9da241929b554f4976eed59159fa2a091031b76"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

fake_users_db = {
    "johndoe": {
        "username": "johndoe",
        "full_name": "John Doe",
        "email": "johndoe@example.com",
        "hashed_password": "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",
    }
}


models.Base.metadata.create_all(bind=engine)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def get_user(db, username: str):
    if username in db:
        user_dict = db[username]
        return UserInDB(**user_dict)

def authenticate_user(fake_db, username: str, password: str):
    user = get_user(fake_db, username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = get_user(fake_users_db, username=token_data.username)
    if user is None:
        raise credentials_exception
    return user


@app.post("/token", response_model=Token)
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()]
):
    user = authenticate_user(fake_users_db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/", include_in_schema=False)
async def redirect_to_docs():
    return RedirectResponse(url="/docs")

@app.get("/files", response_model=list[schemas.File])
def get_files(current_user: Annotated[User, Depends(get_current_user)], db: Session = Depends(get_db)):
    files = crud.get_files(db)
    return files

@app.get("/files/{file_id}/annotations/", response_model=list[schemas.Annotation])
def get_file_annotations(current_user: Annotated[User, Depends(get_current_user)], file_id: int, db: Session = Depends(get_db)):
    annotations = crud.get_annotations(db, file_id=file_id)
    return annotations

@app.get("/files/{file_id}/data", response_model=list[schemas.Annotation])
def get_file(current_user: Annotated[User, Depends(get_current_user)], file_id: int, db: Session = Depends(get_db)):
    file = crud.get_file(db, file_id=file_id)
    file_path = os.path.join('data', file.path)
    if os.path.exists(file_path):
        return FileResponse(path=file_path, media_type='application/octet-stream', status_code=status.HTTP_200_OK)
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='File not found')

@app.post("/files")
def create_upload_file(current_user: Annotated[User, Depends(get_current_user)], file: UploadFile, db: Session = Depends(get_db)):
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
def create_annotations(current_user: Annotated[User, Depends(get_current_user)], annotation: schemas.AnnotationCreate, db: Session = Depends(get_db)):
    annotation = crud.create_annotation(db, annotation=annotation)
    return annotation

@app.delete("/annotations/{annotation_id}")
def delete_annotations(current_user: Annotated[User, Depends(get_current_user)], annotation_id: int, db: Session = Depends(get_db)):
    annotation = crud.delete_annotation(db, annotation_id)
    if annotation:
        return annotation
    else:
        raise HTTPException(status_code=404, detail="Annotation not found")

connected_websockets = set()
latest_message = None
@app.websocket("/files/{file_id}/annotations")
async def websocket_endpoint(websocket: WebSocket, file_id: int, db: Session = Depends(get_db)):
    global latest_message
    await websocket.accept()
    connected_websockets.add(websocket)
    if latest_message:
        try:
            await websocket.send_json(latest_message)
        except WebSocketDisconnect:
            print("Websocket disconnected")
    try:
        while True:
            message = await websocket.receive_text()
            print(message)
            annotations_orm = crud.get_annotations(db, file_id=file_id)
            annotations = [annotation.dict() for annotation in annotations_orm]
            latest_message = annotations
            for ws in connected_websockets:
                try:
                    print(ws)
                    await ws.send_json(annotations)
                except WebSocketDisconnect:
                    print("Websocket disconnected")
                    connected_websockets.remove(ws)
            # await websocket.send_json(annotations)
            # await asyncio.sleep(5)
    except WebSocketDisconnect:
        print("Websocket disconnected")
    finally:
        connected_websockets.remove(websocket)