from app.database import Base
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Integer
from datetime import datetime

class Materia(Base):
    __tablename__ = "materias"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    nome: Mapped[str]
    descricao: Mapped[str | None]
    cor: Mapped[str | None]
    data_criacao: Mapped[datetime] = mapped_column(default=datetime.now)
