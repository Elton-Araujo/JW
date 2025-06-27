from flask import Flask, jsonify
from bs4 import BeautifulSoup
import requests
import re

app = Flask(__name__)

@app.route('/')
def home():
    return jsonify({"message": "API JW funcionando corretamente."})

@app.route('/reuniao')
def reuniao():
    url = "https://wol.jw.org/pt/wol/meetings/r5/lp-t/2025/27"
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")

    semana = soup.select_one("h1.themeScrp").text.strip()
    capitulo = soup.select_one("h2.themeScrp").text.strip()

    def extrair_bloco(nome_secao):
        secao = soup.find("h3", string=re.compile(nome_secao, re.IGNORECASE))
        if not secao:
            return []
        ul = secao.find_next_sibling("ul")
        if not ul:
            return []
        itens = ul.find_all("li")
        resultados = []
        for i, li in enumerate(itens):
            texto = li.get_text(" ", strip=True)
            tempo = re.search(r"\((\d+ min)\)", texto)
            tempo_str = f" ({tempo.group(1)})" if tempo else ""
            titulo = re.sub(r"\(.*?\)", "", texto).strip()
            titulo = re.sub(r"\s+", " ", titulo)
            resultados.append(f"{i + 1}. {titulo}{tempo_str}")
        return resultados

    def extrair_instrutores():
        secao = soup.find("h3", string=re.compile("Sejamos Melhores Instrutores", re.IGNORECASE))
        if not secao:
            return []
        itens = secao.find_all_next("li", limit=3)
        resultados = []
        for i, li in enumerate(itens):
            texto = li.get_text(" ", strip=True)
            tempo = re.search(r"\((\d+ min)\)", texto)
            tempo_str = f" ({tempo.group(1)})" if tempo else ""
            titulo = re.sub(r"\(.*?\)", "", texto).strip()
            titulo = re.sub(r"\s+", " ", titulo)
            resultados.append(f"{i + 4}. {titulo}{tempo_str}")
        return resultados

    def extrair_musica(numero):
        tag = soup.find("h3", string=re.compile(f"Cântico {numero}"))
        return f"Cântico {numero}" if tag else ""

    dados = {
        "semana": semana,
        "capitulo": capitulo,
        "musica_inicial": extrair_musica(131),
        "tesouros": extrair_bloco("Tesouros da Palavra de Deus"),
        "instrutores": extrair_instrutores(),
        "musica_vida_crista": extrair_musica(78),
        "vida_crista": extrair_bloco("Nossa Vida Cristã"),
        "musica_final": extrair_musica(150),
        "url_origem": url
    }

    return jsonify(dados)

if __name__ == '__main__':
    app.run()
