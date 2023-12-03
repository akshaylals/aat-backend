from pydantic import BaseModel


class File(BaseModel):
    id: int
    path: str

    class Config:
        orm_mode = True


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
