from pydantic import BaseModel


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str | None = None


class UserBase(BaseModel):
    username: str
    full_name: str | None = None


class UserCreate(UserBase):
    hashed_password: str


class User(UserBase):
    id: int

    class Config:
        orm_mode = True


class UserAuth(UserBase):
    id: int
    hashed_password: str

    class Config:
        orm_mode = True


class ProjectBase(BaseModel):
    path: str


class Project(ProjectBase):
    id: int
    owner: User

    class Config:
        orm_mode = True


class ProjectCreate(ProjectBase):
    owner_id: int


class AnnotationBase(BaseModel):
    note: str
    coordinates: dict
    project_id: int


class AnnotationCreate(AnnotationBase):
    pass


class Annotation(AnnotationBase):
    id: int
    
    class Config:
        orm_mode = True
