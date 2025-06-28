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

    # Detectar todos os cânticos da reunião
    def detectar_canticos():
        h3_tags = soup.find_all("h3", string=re.compile(r"Cântico \d+"))
        encontrados = []
        for tag in h3_tags:
            match = re.search(r"Cântico \d+", tag.text)
            if match:
                encontrados.append(match.group(0))
        return encontrados

    canticos = detectar_canticos()
    musica_inicial = canticos[0] if len(canticos) > 0 else ""
    musica_vida_crista = canticos[1] if len(canticos) > 1 else ""
    musica_final = canticos[2] if len(canticos) > 2 else ""

    # Extrair os itens numerados
    def extract_itens_by_range(start, end):
        result = []
        count = 0
        h3_tags = soup.find_all("h3")
        for h3 in h3_tags:
            texto = h3.get_text(" ", strip=True)
            match = re.match(rf"^({start + count})\.", texto)
            if match:
                tempo_tag = h3.find_next("p")
                tempo = ""
                if tempo_tag and "min" in tempo_tag.text:
                    tempo = tempo_tag.text.strip().replace("(", "").replace(")", "")
                nome = texto.strip()
                item = f"{nome} ({tempo})" if tempo and tempo not in nome else nome
                result.append(item)
                count += 1
            if count > (end - start):
                break
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
