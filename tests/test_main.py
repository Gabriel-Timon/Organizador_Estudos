from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_rota_raiz():
    response = client.get("/")

    assert response.status_code == 200
    assert response.json() == {"mensagem": "Bem vindo(a) ao Organizador de Estudos"}


def test_criar_materia_com_nome_vazio():
    response = client.post("/materias", json={"nome": "   ", "descricao": None, "cor": None})

    assert response.status_code == 422
    