import json
import os

PROFILE_PATH = "profiles.json"

def carregar_todos_perfis():
    if not os.path.exists(PROFILE_PATH):
        return {}
    with open(PROFILE_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def salvar_perfil(nome: str, dados: dict):
    perfis = carregar_todos_perfis()
    perfis[nome] = dados
    with open(PROFILE_PATH, "w", encoding="utf-8") as f:
        json.dump(perfis, f, indent=2)

def carregar_perfil(nome: str):
    perfis = carregar_todos_perfis()
    return perfis.get(nome)

def listar_perfis():
    return list(carregar_todos_perfis().keys())

