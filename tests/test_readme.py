"""
O diagrama de arquitetura do README.md (MG5) não fica velho sem ninguém ver: todo arquivo que ele cita existe,
o modelo do Gemini é o do código e o PNG (para o documento e os slides) está em docs/.
"""
import re
from pathlib import Path

from raiox.ia import MODELO

RAIZ = Path(__file__).resolve().parent.parent
README = (RAIZ / "README.md").read_text(encoding="utf-8")


def _diagrama():
    bloco = re.search(r"```mermaid\n(.*?)```", README, re.S)
    assert bloco, "o README perdeu o bloco mermaid da seção Arquitetura"
    return bloco.group(1)


def test_diagrama_so_cita_arquivos_que_existem():
    caminhos = set(re.findall(r"[\w*-]+(?:/[\w*-]+)*\.(?:py|tf|yml)", _diagrama()))
    assert len(caminhos) >= 8                              # a busca achou os arquivos (não passa por estar vazia)
    if not (RAIZ / ".git").exists():                       # dentro do contêiner: o .dockerignore deixa a infra/ fora
        caminhos = {c for c in caminhos if not c.startswith("infra/")}   # da imagem (o CI confere a infra/ inteira)
    faltando = sorted(c for c in caminhos if not any(RAIZ.glob(c)))
    assert faltando == []                                  # renomeou ou apagou? atualize o diagrama e o PNG


def test_diagrama_usa_o_modelo_do_codigo():
    assert MODELO in _diagrama()                           # trocou o modelo em raiox/ia.py? troque no diagrama


def test_readme_aponta_para_o_png_da_arquitetura():
    assert "(docs/arquitetura.png)" in README
    assert (RAIZ / "docs" / "arquitetura.png").stat().st_size > 10_000
