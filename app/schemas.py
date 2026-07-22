from pydantic import BaseModel

class CreateMaterias(BaseModel):
    nome: str
    descricao: str = "Sem descrição"
    cor: str = "Sem cor"