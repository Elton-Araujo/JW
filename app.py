from flask import Flask, jsonify
import requests
from bs4 import BeautifulSoup
import re

app = Flask(__name__)

@app.route('/reuniao/<int:ano>/<int:semana>', methods=['GET'])
def get_reuniao(ano, semana):
    url = f'https://wol.jw.org/pt/wol/meetings/r5/lp-t/{ano}/{semana}'
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')

    def get_text(selector):
        tag = soup.select_one(selector)
        return tag.get_text(strip=True) if tag else ""

    semana = get_text("h1")
    capitulo = get_text("h2")

    def detectar_canticos_ordenados():
        tags = soup.find_all(string=re.compile(r"Cântico \d+"))
        vistos = set()
        canticos = []
        for tag in tags:
            match = re.search(r"Cântico \d+", tag)
            if match:
                c = match.group(0)
                if c not in vistos:
                    canticos.append(c)
                    vistos.add(c)
        return canticos

    canticos = detectar_canticos_ordenados()
    musica_inicial = canticos[0] if len(canticos) > 0 else ""
    musica_vida_crista = canticos[1] if len(canticos) > 1 else ""
    musica_final = canticos[2] if len(canticos) > 2 else ""

    def extrair_titulo_com_tempo(titulo, tempo_texto):
        match_tempo = re.search(r"\(\s*(\d+)\s*min\s*\)", tempo_texto)
        if match_tempo:
            tempo = match_tempo.group(0).strip()
            return f"{titulo} {tempo}"
        return titulo.strip()

    def extract_itens_by_range(start, end):
        result = []
        h3_tags = soup.find_all("h3")
        for count, h3 in enumerate(h3_tags, start=1):
            texto = h3.get_text(" ", strip=True)
            if start <= count <= end:
                p = h3.find_next_sibling("p")
                tempo_texto = p.get_text(strip=True) if p else ""
                item = extrair_titulo_com_tempo(texto, tempo_texto)
                result.append(item)
        return result

    tesouros = extract_itens_by_range(1, 3)
    instrutores = extract_itens_by_range(4, 6)
    vida_crista = extract_itens_by_range(7, 9)

    return jsonify({
        "semana": semana,
        "capitulo": capitulo,
        "musica_inicial": musica_inicial,
        "tesouros": tesouros,
        "instrutores": instrutores,
        "musica_vida_crista": musica_vida_crista,
        "vida_crista": vida_crista,
        "musica_final": musica_final,
        "url_origem": url
    })

if __name__ == '__main__':
    app.run(debug=True)
