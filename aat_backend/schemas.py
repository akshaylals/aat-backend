from pydantic import BaseModel


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str | None = None


class User(BaseModel):
    username: str
    email: str | None = None
    full_name: str | None = None


class UserInDB(User):
    hashed_password: str


class FileBase(BaseModel):
    path: str


class File(FileBase):
    id: int

    class Config:
        orm_mode = True


class FileCreate(FileBase):
    pass


class AnnotationBase(BaseModel):
    note: str
    coordinates: dict
    file_id: int


class AnnotationCreate(AnnotationBase):
    pass


class Annotation(AnnotationBase):
    id: int
    
    class Config:
        orm_mode = True
