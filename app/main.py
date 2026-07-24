from app.database import Base, engine, get_db
from app.models import Materia, Tarefa
from app.schemas import CreateMateria, GetMateria, CreateTarefa, GetTarefa
from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session
from sqlalchemy import select

Base.metadata.create_all(bind=engine)

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


@app.get("/materias", response_model=list[GetMateria])
def get_materias(db: Session = Depends(get_db)):
    query = select(Materia)
    return db.execute(query).scalars().all()


@app.get("/materias/{id}", response_model=GetMateria)
def get_materiaByID(id: int, db: Session = Depends(get_db)):
    materia_db = db.get(Materia, id)
    if materia_db is None:
        raise HTTPException(404, "Matéria não encontrada.")

    return materia_db    


@app.put("/materias/{id}", response_model=GetMateria)
def edit_materiaByID(id: int, materia_atualizada: CreateMateria, db: Session = Depends(get_db)):
    materia_db = db.get(Materia, id)
    if materia_db is None:
        raise HTTPException(404, "Matéria não encontrada.")

    materia_db.nome = materia_atualizada.nome
    materia_db.descricao = materia_atualizada.descricao
    materia_db.cor = materia_atualizada.cor

    db.commit()
    db.refresh(materia_db)

    return materia_db


@app.delete("/materias/{id}", status_code=204)
def delete_materiaByID(id: int, db: Session = Depends(get_db)):
    materia_db = db.get(Materia, id)
    if materia_db is None:
        raise HTTPException(404, "Matéria não encontrada.")

    db.delete(materia_db)
    db.commit()


@app.post("/tarefas", response_model=GetTarefa)
def create_tarefa(tarefa: CreateTarefa, db: Session = Depends(get_db)):
    busca = db.get(Materia, tarefa.materia_id)
    if busca is None:
        raise HTTPException(404, "Materia não encontrada.")

    dados = tarefa.model_dump()
    item = Tarefa(**dados)

    db.add(item)
    db.commit()
    db.refresh(item)

    return item
