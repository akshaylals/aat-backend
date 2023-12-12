from pydantic import BaseModel


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
