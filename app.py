from flask import Flask, jsonify
import requests
from bs4 import BeautifulSoup

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

    # Música inicial
    musica_inicial_tag = soup.find("h3", string=lambda x: x and "Comentários iniciais" in x)
    musica_inicial = "Cântico 131" if musica_inicial_tag else ""

    # Música final
    musica_final_tag = soup.find("h3", string=lambda x: x and "Comentários finais" in x)
    musica_final = "Cântico 150" if musica_final_tag else ""

    # Música depois dos instrutores
    musica_vida_crista_tag = soup.find("h3", string=lambda x: x and "Cântico 78" in x)
    musica_vida_crista = "Cântico 78" if musica_vida_crista_tag else ""

    # Extrair itens numerados com tempo (ex: 1. Tema (10 min))
    def extract_itens_by_range(start, end):
        result = []
        for i in range(start, end + 1):
            h3 = soup.find("h3", string=lambda x: x and x.strip().startswith(f"{i}."))
            if not h3:
                continue
            texto = h3.get_text(" ", strip=True)
            tempo_tag = h3.find_next("p")
            tempo = ""
            if tempo_tag and "min" in tempo_tag.text:
                tempo = tempo_tag.text.strip().replace("(", "").replace(")", "")
            nome = texto.split("(")[0].strip()
            result.append(f"{i}. {nome} ({tempo})" if tempo else f"{i}. {nome}")
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
