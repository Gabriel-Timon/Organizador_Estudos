from app.database import Base
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Integer

class Materia(Base):
    __tablename__ = "materias"
    nome: Mapped[str]
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
