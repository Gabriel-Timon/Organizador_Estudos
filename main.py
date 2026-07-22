from fastapi import FastAPI

materias = []

app = FastAPI()

@app.get("/")
def root():
    return "Bem vindo(a) ao Organiador de Estudos"


@app.post("/meterias")
def create_materia(materia: str):
    materias.append(materia)


@app.get("/materias")
def get_materias():
    return materias


@app.get("/materias/{id}")
def get_materiaByID(id: int) -> str:
    item = materias[id]
    return item
