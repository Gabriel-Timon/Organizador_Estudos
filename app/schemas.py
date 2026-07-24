from pydantic import BaseModel, ConfigDict, field_validator
from datetime import datetime, date
from typing import Literal

class CreateMateria(BaseModel):
    nome: str
    descricao: str | None = None
    cor: str | None = None

    @field_validator('nome')
    @classmethod
    def tratar_string_vazia(cls, nome: str) -> str:
        if nome.strip() == "":
            raise ValueError("O nome da matéria não pode ser vazio.")
        return nome.strip()


class GetMateria(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nome: str
    descricao: str | None
    cor: str | None
    data_criacao: datetime


class CreateTarefa(BaseModel):
    titulo: str
    descricao: str | None = None
    materia_id: int
    prioridade: Literal["baixa", "media", "alta"]
    data_limite: date | None = None

    @field_validator("titulo")
    @classmethod
    def tratar_string_vazia(cls, titulo: str) -> str:
        if titulo.strip() == "":
            raise ValueError("O título da tarefa não pode ser vazio.")
        return titulo.strip()


class GetTarefa(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    titulo: str
    descricao: str | None
    materia_id: int
    prioridade: Literal["baixa", "media", "alta"]
    data_limite: date | None
    status: Literal["pendente", "em_andamento", "concluida"]
    data_criacao: datetime
    data_conclusao: datetime | None
