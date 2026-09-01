from __future__ import annotations

from app.database import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, ForeignKey
from datetime import datetime, date

class Materia(Base):
    __tablename__ = "materias"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    nome: Mapped[str]
    descricao: Mapped[str | None]
    cor: Mapped[str | None]
    data_criacao: Mapped[datetime] = mapped_column(default=datetime.now)
    tarefas: Mapped[list[Tarefa]] = relationship(back_populates="materia")
    sessoes: Mapped[list[SessaoEstudo]] = relationship(back_populates="materia")


class Tarefa(Base):
    __tablename__ = "tarefas"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    materia_id: Mapped[int] = mapped_column(ForeignKey("materias.id"))
    titulo: Mapped[str]
    descricao: Mapped[str | None]
    data_limite: Mapped[date | None]
    data_criacao: Mapped[datetime] = mapped_column(default=datetime.now)
    data_conclusao: Mapped[datetime | None]
    prioridade: Mapped[str]
    status: Mapped[str] = mapped_column(default="pendente")
    materia: Mapped[Materia] = relationship(back_populates="tarefas")


class SessaoEstudo(Base):
    __tablename__ = "sessoes"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    materia_id: Mapped[int] = mapped_column(ForeignKey("materias.id"))
    data: Mapped[date]
    duracao_minutos: Mapped[int]
    observacao: Mapped[str | None]
    materia: Mapped[Materia] = relationship(back_populates="sessoes")
