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

    titulo = get_text("h1")
    semana, capitulo = titulo.split(" | ") if " | " in titulo else ("", "")

    musica_inicial = get_text(".opening-song")
    introducao = get_text(".opening-comments")

    def get_lista_por_icone(icone):
        img = soup.find("img", {"src": lambda v: v and icone in v})
        if not img:
            return []
        ul = img.find_next("ul")
        return [li.get_text(strip=True) for li in ul.find_all("li")] if ul else []

    tesouros = get_lista_por_icone("treasures")
    instrutores = get_lista_por_icone("ministry")
    vida_crista = get_lista_por_icone("christian-life")

    musica_final = get_text(".concluding-song")

    return jsonify({
        "semana": semana,
        "capitulo": capitulo,
        "musica_inicial": musica_inicial,
        "introducao": introducao,
        "tesouros": tesouros,
        "instrutores": instrutores,
        "vida_crista": vida_crista,
        "musica_final": musica_final,
        "url_origem": url
    })

@app.route('/mes/<int:ano>/<int:mes>', methods=['GET'])
def get_meses(ano, mes):
    url = f'https://wol.jw.org/pt/wol/meetings/r5/lp-t/{ano}/{mes}'
    resp = requests.get(url)
    if resp.status_code != 200:
        return jsonify({"erro": "Mês não encontrado"}), 404

    soup = BeautifulSoup(resp.content, 'html.parser')
    links = soup.select('li a[href*="/lp-t/"]')

    semanas = []
    for a in links:
        href = a.get('href')
        texto = a.get_text(strip=True)
        if not href or not texto:
            continue
        try:
            indice = int(href.rstrip('/').split('/')[-1])
        except ValueError:
            continue

        semanas.append({
            "semana": texto,
            "indice": indice,
            "link": f'https://wol.jw.org{href}'
        })

    return jsonify(semanas)

if __name__ == '__main__':
    app.run(debug=True)
