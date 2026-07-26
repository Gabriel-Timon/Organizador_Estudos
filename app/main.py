from app.database import Base, engine, get_db
from app.models import Materia, Tarefa
from app.schemas import CreateMateria, GetMateria, CreateTarefa, GetTarefa, UpdateTarefa
from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session
from sqlalchemy import select
from typing import Literal
from datetime import datetime, date

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

    if materia_db.tarefas:
        raise HTTPException(409, f"Não foi possível excluir a matéria pois há uma ou várias tarefas vinculadas com {materia_db.nome}")

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


@app.get("/tarefas", response_model=list[GetTarefa])
def get_tarefas(
    materia_id: int | None = None, 
    prioridade: Literal["baixa", "media", "alta"] | None = None,
    status: Literal["pendente", "em_andamento", "concluida"] | None = None,
    atrasadas: bool = False,
    db: Session = Depends(get_db)
):
    
    query = select(Tarefa)

    if materia_id is not None:
        query = query.where(Tarefa.materia_id == materia_id)

    if prioridade is not None:
        query = query.where(Tarefa.prioridade == prioridade)

    if status is not None:
        query = query.where(Tarefa.status == status)

    if atrasadas:
        hoje = date.today()
        query = query.where(hoje > Tarefa.data_limite, Tarefa.status != "concluida")


    return db.execute(query).scalars().all()


@app.get("/tarefas/{id}", response_model=GetTarefa)
def get_tarefaByID(id: int, db: Session = Depends(get_db)):
    tarefa_db = db.get(Tarefa, id)
    if tarefa_db is None:
        raise HTTPException(404, "Tarefa não encontrada.")

    return tarefa_db


@app.put("/tarefas/{id}", response_model=GetTarefa)
def edit_tarefaByID(
    id: int, 
    tarefa_atualizada: UpdateTarefa,
    db: Session = Depends(get_db)
):

    tarefa_db = db.get(Tarefa, id)
    if tarefa_db is None:
        raise HTTPException(404, "Tarefa não encontrada.")

    materia_db = db.get(Materia, tarefa_atualizada.materia_id)
    if materia_db is None:
        raise HTTPException(404, "Matéria não encontrada")


    status_anterior_tarefa = tarefa_db.status
    if tarefa_atualizada.status == "concluida" and status_anterior_tarefa != "concluida":
        tarefa_db.data_conclusao = datetime.now()

    elif tarefa_atualizada.status != "concluida":
        tarefa_db.data_conclusao = None

    tarefa_db.titulo = tarefa_atualizada.titulo
    tarefa_db.descricao = tarefa_atualizada.descricao
    tarefa_db.materia_id = tarefa_atualizada.materia_id
    tarefa_db.prioridade = tarefa_atualizada.prioridade
    tarefa_db.data_limite = tarefa_atualizada.data_limite
    tarefa_db.status = tarefa_atualizada.status

    db.commit()
    db.refresh(tarefa_db)

    return tarefa_db


@app.patch("/tarefas/{id}/concluir", response_model=GetTarefa)
def concluir_tarefa(id: int, db: Session = Depends(get_db)):
    tarefa_db = db.get(Tarefa, id)
    if tarefa_db is None:
        raise HTTPException(404, "A tarefa não foi encontrada.")
    
    if tarefa_db.status != "concluida":
        tarefa_db.data_conclusao = datetime.now()
        tarefa_db.status = "concluida"

    db.commit()
    db.refresh(tarefa_db)

    return tarefa_db


@app.delete("/tarefas/{id}", status_code=204)
def delete_tarefa(id: int, db: Session = Depends(get_db)):
    tarefa_db = db.get(Tarefa, id)
    if tarefa_db is None:
        raise HTTPException(404, "Tarefa não encontrada.")

    db.delete(tarefa_db)
    db.commit()
