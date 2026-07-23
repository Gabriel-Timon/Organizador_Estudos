from pydantic import BaseModel, ConfigDict
from datetime import datetime

class CreateMateria(BaseModel):
    nome: str
    descricao: str | None = None
    cor: str | None = None


class GetMateria(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nome: str
    descricao: str | None
    cor: str | None
    data_criacao: datetime