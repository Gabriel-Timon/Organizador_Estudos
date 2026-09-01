from datetime import date, timedelta

from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def criar_materia(nome: str = "Matemática") -> dict:
    response = client.post(
        "/materias",
        json={"nome": nome, "descricao": "Conteúdos da disciplina", "cor": "#2563EB"},
    )
    assert response.status_code == 200
    return response.json()


def criar_tarefa(materia_id: int, **overrides) -> dict:
    payload = {
        "titulo": "Revisar conteúdo",
        "descricao": "Resolver exercícios da lista",
        "materia_id": materia_id,
        "prioridade": "alta",
        "data_limite": None,
    }
    payload.update(overrides)
    response = client.post("/tarefas", json=payload)
    assert response.status_code == 200
    return response.json()


def criar_sessao(materia_id: int, **overrides) -> dict:
    payload = {
        "materia_id": materia_id,
        "data": date.today().isoformat(),
        "duracao_minutos": 60,
        "observacao": "Estudo focado",
    }
    payload.update(overrides)
    response = client.post("/sessoes", json=payload)
    assert response.status_code == 200
    return response.json()


def test_rota_raiz():
    response = client.get("/")

    assert response.status_code == 200
    assert response.json() == {"mensagem": "Bem vindo(a) ao Organizador de Estudos"}


def test_criar_materia_normaliza_nome_e_permite_crud_completo():
    response = client.post(
        "/materias",
        json={"nome": "  Física  ", "descricao": "Mecânica", "cor": "#10B981"},
    )
    materia = response.json()

    assert response.status_code == 200
    assert materia["nome"] == "Física"
    assert materia["descricao"] == "Mecânica"
    assert materia["data_criacao"]

    assert client.get("/materias").json() == [materia]
    assert client.get(f"/materias/{materia['id']}").json() == materia

    atualizada = client.put(
        f"/materias/{materia['id']}",
        json={"nome": "Física II", "descricao": None, "cor": None},
    )
    assert atualizada.status_code == 200
    assert atualizada.json()["nome"] == "Física II"

    assert client.delete(f"/materias/{materia['id']}").status_code == 204
    assert client.get(f"/materias/{materia['id']}").status_code == 404


def test_materia_rejeita_nome_vazio_e_retorna_404_quando_nao_existe():
    response = client.post(
        "/materias", json={"nome": "   ", "descricao": None, "cor": None}
    )

    assert response.status_code == 422
    assert client.get("/materias/999").status_code == 404
    assert client.put(
        "/materias/999", json={"nome": "Nova", "descricao": None, "cor": None}
    ).status_code == 404
    assert client.delete("/materias/999").status_code == 404


def test_materia_nao_pode_ser_excluida_com_tarefa_ou_sessao_vinculada():
    materia = criar_materia()
    criar_tarefa(materia["id"])

    response = client.delete(f"/materias/{materia['id']}")
    assert response.status_code == 409
    assert "tarefas vinculadas" in response.json()["detail"]

    tarefa = client.get("/tarefas").json()[0]
    assert client.delete(f"/tarefas/{tarefa['id']}").status_code == 204
    criar_sessao(materia["id"])

    response = client.delete(f"/materias/{materia['id']}")
    assert response.status_code == 409
    assert "sessões de estudo vinculadas" in response.json()["detail"]


def test_tarefas_validam_materia_e_titulo():
    response = client.post(
        "/tarefas",
        json={
            "titulo": "   ",
            "materia_id": 1,
            "prioridade": "alta",
            "data_limite": None,
        },
    )
    assert response.status_code == 422

    response = client.post(
        "/tarefas",
        json={
            "titulo": "Tarefa válida",
            "materia_id": 999,
            "prioridade": "alta",
            "data_limite": None,
        },
    )
    assert response.status_code == 404


def test_tarefas_permite_filtros_atualizacao_conclusao_e_exclusao():
    materia = criar_materia()
    tarefa = criar_tarefa(
        materia["id"],
        titulo="Prova de cálculo",
        data_limite=(date.today() - timedelta(days=1)).isoformat(),
    )

    assert tarefa["status"] == "pendente"
    assert client.get(f"/tarefas/{tarefa['id']}").json()["titulo"] == "Prova de cálculo"
    filtradas = client.get(
        "/tarefas",
        params={
            "materia_id": materia["id"],
            "prioridade": "alta",
            "status": "pendente",
            "atrasadas": "true",
        },
    )
    assert [item["id"] for item in filtradas.json()] == [tarefa["id"]]

    atualizada = client.put(
        f"/tarefas/{tarefa['id']}",
        json={
            "titulo": "Prova de cálculo revisada",
            "descricao": "Lista final",
            "materia_id": materia["id"],
            "prioridade": "media",
            "data_limite": date.today().isoformat(),
            "status": "em_andamento",
        },
    )
    assert atualizada.status_code == 200
    assert atualizada.json()["data_conclusao"] is None

    concluida = client.patch(f"/tarefas/{tarefa['id']}/concluir")
    assert concluida.status_code == 200
    assert concluida.json()["status"] == "concluida"
    assert concluida.json()["data_conclusao"] is not None

    assert client.get("/tarefas", params={"status": "concluida"}).json()[0]["id"] == tarefa[
        "id"
    ]
    assert client.delete(f"/tarefas/{tarefa['id']}").status_code == 204
    assert client.get(f"/tarefas/{tarefa['id']}").status_code == 404


def test_tarefas_retorna_404_para_registros_inexistentes():
    assert client.get("/tarefas/999").status_code == 404
    assert client.put(
        "/tarefas/999",
        json={
            "titulo": "Tarefa",
            "materia_id": 1,
            "prioridade": "baixa",
            "data_limite": None,
            "status": "pendente",
        },
    ).status_code == 404
    assert client.patch("/tarefas/999/concluir").status_code == 404
    assert client.delete("/tarefas/999").status_code == 404


def test_sessoes_validam_dados_listam_por_materia_e_permite_exclusao():
    materia = criar_materia()

    assert client.post(
        "/sessoes",
        json={
            "materia_id": materia["id"],
            "data": date.today().isoformat(),
            "duracao_minutos": 0,
        },
    ).status_code == 422
    assert client.post(
        "/sessoes",
        json={
            "materia_id": materia["id"],
            "data": (date.today() + timedelta(days=1)).isoformat(),
            "duracao_minutos": 30,
        },
    ).status_code == 422
    assert client.post(
        "/sessoes",
        json={
            "materia_id": 999,
            "data": date.today().isoformat(),
            "duracao_minutos": 30,
        },
    ).status_code == 404

    sessao = criar_sessao(materia["id"], duracao_minutos=90)
    assert client.get("/sessoes", params={"materia_id": materia["id"]}).json() == [sessao]
    assert client.delete(f"/sessoes/{sessao['id']}").status_code == 204
    assert client.delete(f"/sessoes/{sessao['id']}").status_code == 404


def test_relatorios_resumem_tarefas_e_sessoes():
    matematica = criar_materia("Matemática")
    historia = criar_materia("História")
    concluida = criar_tarefa(
        matematica["id"], data_limite=(date.today() - timedelta(days=1)).isoformat()
    )
    criar_tarefa(
        historia["id"], data_limite=(date.today() - timedelta(days=1)).isoformat()
    )
    assert client.patch(f"/tarefas/{concluida['id']}/concluir").status_code == 200

    criar_sessao(matematica["id"], duracao_minutos=60)
    criar_sessao(
        matematica["id"],
        data=(date.today() - timedelta(days=1)).isoformat(),
        duracao_minutos=30,
    )
    criar_sessao(
        historia["id"],
        data=(date.today() - timedelta(days=10)).isoformat(),
        duracao_minutos=120,
    )

    resumo = client.get("/relatorios/resumo")
    assert resumo.status_code == 200
    assert resumo.json() == {
        "tarefas_concluidas": 1,
        "tarefas_pendentes": 1,
        "tarefas_atrasadas": 1,
        "materia_mais_estudada": "História",
        "total_estudado_minutos": 210,
        "media_diaria_ultimos_sete_dias": 12.9,
    }

    por_materia = client.get("/relatorios/tempo-por-materia")
    assert sorted(por_materia.json(), key=lambda item: item["materia"]) == [
        {"materia": "História", "total_minutos": 120},
        {"materia": "Matemática", "total_minutos": 90},
    ]

    ultimos_dias = client.get("/relatorios/ultimos-7-dias")
    assert ultimos_dias.json() == [
        {
            "data": (date.today() - timedelta(days=1)).isoformat(),
            "total_minutos": 30,
        },
        {"data": date.today().isoformat(), "total_minutos": 60},
    ]


def test_relatorios_sem_dados_retorna_valores_vazios_consistentes():
    assert client.get("/relatorios/resumo").json() == {
        "tarefas_concluidas": 0,
        "tarefas_pendentes": 0,
        "tarefas_atrasadas": 0,
        "materia_mais_estudada": None,
        "total_estudado_minutos": 0,
        "media_diaria_ultimos_sete_dias": 0.0,
    }
    assert client.get("/relatorios/tempo-por-materia").json() == []
    assert client.get("/relatorios/ultimos-7-dias").json() == []
