from flask import Flask, jsonify
from bs4 import BeautifulSoup
import requests
import re

app = Flask(__name__)

@app.route('/')
def home():
    return jsonify({"message": "API JW funcionando corretamente."})

@app.route('/reuniao/<int:ano>/<int:semana>')
def reuniao(ano, semana):
    url = f"https://wol.jw.org/pt/wol/meetings/r5/lp-t/{ano}/{semana}"
    response = requests.get(url)

    if response.status_code != 200:
        return jsonify({"error": "Página não encontrada", "status": response.status_code}), 404

    soup = BeautifulSoup(response.content, "html.parser")

    semana_texto = soup.select_one("h1.themeScrp")
    capitulo_texto = soup.select_one("h2.themeScrp")
    
    if not semana_texto or not capitulo_texto:
        return jsonify({"error": "Conteúdo da reunião não encontrado"}), 404

    semana = semana_texto.text.strip()
    capitulo = capitulo_texto.text.strip()

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
