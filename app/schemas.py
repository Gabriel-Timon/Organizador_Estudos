from pydantic import BaseModel, ConfigDict, field_validator
from datetime import datetime

class CreateMateria(BaseModel):
    nome: str
    descricao: str | None = None
    cor: str | None = None

    @field_validator('nome')
    @classmethod
    def tratar_string_vazia(cls, nome: str):
        if nome.strip() == "":
            raise ValueError("O nome não pode ser vazio.")
        return nome.strip()


class GetMateria(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nome: str
    descricao: str | None
    cor: str | None
    data_criacao: datetime