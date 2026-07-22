from pydantic import BaseModel

class CreateMateria(BaseModel):
    nome: str
    descricao: str | None = None
    cor: str | None = None