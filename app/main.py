from app.schemas import (
    CreateMateria, 
    GetMateria, 
    CreateTarefa, 
    GetTarefa, 
    UpdateTarefa,
    CreateSessaoEstudo,
    GetSessaoEstudo,
    GetResumoRelatorio,
    GetEstudoPorDia,
    GetTempoPorMateria
    )
from app.database import Base, engine, get_db
from app.models import Materia, Tarefa, SessaoEstudo
from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session
from sqlalchemy import select, func
from typing import Literal
from datetime import datetime, date, timedelta

Base.metadata.create_all(bind=engine)

app = FastAPI()

@app.get("/")
def root():
    return {"mensagem": "Bem vindo(a) ao Organizador de Estudos"}


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

    if materia_db.sessoes:
        raise HTTPException(409, f"Não foi possível excluir a matéria pois há uma ou várias sessões de estudo vinculadas com {materia_db.nome}")

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


@app.post("/sessoes", response_model=GetSessaoEstudo)
def create_sessao_estudo(sessao_estudo: CreateSessaoEstudo, db: Session = Depends(get_db)):
    busca = db.get(Materia, sessao_estudo.materia_id)
    if busca is None:
        raise HTTPException(404, "Matéria não encontrada.")

    dados = sessao_estudo.model_dump()
    item = SessaoEstudo(**dados)

    db.add(item)
    db.commit()
    db.refresh(item)

    return item


@app.get("/sessoes", response_model=list[GetSessaoEstudo])
def get_sessoes_estudo(materia_id: int | None = None, db: Session = Depends(get_db)):
    query = select(SessaoEstudo)

    if materia_id is not None:
        query = query.where(SessaoEstudo.materia_id == materia_id)

    return db.execute(query).scalars().all()


@app.delete("/sessoes/{id}", status_code=204)
def delete_sessao(id: int, db: Session = Depends(get_db)):
    sessao_estudo = db.get(SessaoEstudo, id)
    if sessao_estudo is None:
        raise HTTPException(404, "Sessão não encontrada.")

    db.delete(sessao_estudo)
    db.commit()


@app.get("/relatorios/resumo", response_model=GetResumoRelatorio)
def tempo_total_estudado(db: Session = Depends(get_db)):
    data_inicial = date.today() - timedelta(days=6)

    total_por_materia = func.sum(SessaoEstudo.duracao_minutos).label("total_minutos")

    query_duracao_minutos = select(func.sum(SessaoEstudo.duracao_minutos))
    query_tarefas_concluidas = select(func.count(Tarefa.id)).where(Tarefa.status == "concluida")
    query_tarefas_pendentes = select(func.count(Tarefa.id)).where(Tarefa.status != "concluida")
    query_tarefas_atrasadas = select(func.count(Tarefa.id)).where(Tarefa.status != "concluida", Tarefa.data_limite < date.today())
    query_materia_mais_estudada = select(Materia.nome, total_por_materia).join(SessaoEstudo, SessaoEstudo.materia_id == Materia.id).group_by(Materia.id, Materia.nome).order_by(total_por_materia.desc()).limit(1)
    query_soma_sete_dias = select(
        func.sum(SessaoEstudo.duracao_minutos)
    ).where(
        data_inicial <= SessaoEstudo.data
    )

    
    total_minutos = db.scalar(query_duracao_minutos)
    tarefas_concluidas = db.scalar(query_tarefas_concluidas)
    tarefas_pendentes = db.scalar(query_tarefas_pendentes)
    tarefas_atrasadas = db.scalar(query_tarefas_atrasadas)
    soma_sete_dias = db.scalar(query_soma_sete_dias)
    resultado = db.execute(query_materia_mais_estudada).first()

    if total_minutos is None:
        total_minutos = 0

    if resultado is None:
        materia_mais_estudada = None
    else:
        materia_mais_estudada = resultado.nome

    if soma_sete_dias is None:
        soma_sete_dias = 0

    return {
        "tarefas_concluidas": tarefas_concluidas,
        "tarefas_pendentes": tarefas_pendentes,
        "tarefas_atrasadas": tarefas_atrasadas,
        "materia_mais_estudada": materia_mais_estudada,
        "total_estudado_minutos": total_minutos,
        "media_diaria_ultimos_sete_dias": round(soma_sete_dias / 7, 1)
        }


@app.get("/relatorios/tempo-por-materia", response_model=list[GetTempoPorMateria])
def tempo_por_materia(db: Session = Depends(get_db)):
    query = select(
        Materia.nome,
        func.sum(SessaoEstudo.duracao_minutos).label("total_minutos")
    ).join(
        SessaoEstudo,
        SessaoEstudo.materia_id == Materia.id
    ).group_by(
        Materia.id,
        Materia.nome
    )

    resultados = db.execute(query).all()

    return [
        {
            "materia": linha.nome,
            "total_minutos": linha.total_minutos
        }
        for linha in resultados
    ]


@app.get("/relatorios/ultimos-7-dias", response_model=list[GetEstudoPorDia])
def ultimos_sete_dias(db: Session = Depends(get_db)):
    data_inicial = date.today() - timedelta(days=6)
    query = select(
        SessaoEstudo.data,
        func.sum(SessaoEstudo.duracao_minutos).label("total_minutos")
    ).where(
        SessaoEstudo.data >= data_inicial
    ).group_by(
        SessaoEstudo.data
    ).order_by(
        SessaoEstudo.data
    )

    resultados = db.execute(query).all()

    return [
        {
            "data": linha.data,
            "total_minutos": linha.total_minutos
        }
        for linha in resultados
    ]


