import app.models
from app.database import Base, engine
from fastapi import FastAPI, HTTPException
from app.schemas import CreateMateria

Base.metadata.create_all(bind=engine)

materias = []
ultimo_id = 1

app = FastAPI()

@app.get("/")
def root():
    return "Bem vindo(a) ao Organiador de Estudos"


@app.post("/materias")
def create_materia(materia: CreateMateria):
    global ultimo_id
    item = {
        "id": ultimo_id,
        "nome": materia.nome,
        "descricao": materia.descricao,
        "cor": materia.cor
        }
    ultimo_id += 1
    materias.append(item)
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
