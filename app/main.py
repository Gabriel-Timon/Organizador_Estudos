import app.models
from app.database import Base, engine, get_db
from app.models import Materia
from app.schemas import CreateMateria, GetMateria
from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session

Base.metadata.create_all(bind=engine)

materias = []
ultimo_id = 1

app = FastAPI()

@app.get("/")
def root():
    return "Bem vindo(a) ao Organiador de Estudos"


@app.post("/materias", response_model=GetMateria)
def create_materia(materia: CreateMateria, db: Session = Depends(get_db)):
    item = Materia(
        nome=materia.nome,
        descricao=materia.descricao,
        cor=materia.cor
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    
    return item


@app.get("/materias")
def get_materias():
    return materias


@app.get("/materias/{id}")
def get_materiaByID(id: int):
    for m in materias:
        if m["id"] == id:
            return m
      
    raise HTTPException(404, "O id da matéria não existe")
