from fastapi import FastAPI, HTTPException
from app.schemas import *

materias = []

app = FastAPI()

@app.get("/")
def root():
    return "Bem vindo(a) ao Organiador de Estudos"


@app.post("/materias")
def create_materia(materia: CreateMaterias):
    item = {
        "nome": materia.nome,
        "descricao": materia.descricao,
        "cor": materia.cor
        }
    materias.append(item)


@app.get("/materias")
def get_materias():
    return materias


@app.get("/materias/{id}")
def get_materiaByID(id: int) -> str:
    item = materias[id]
    return item
