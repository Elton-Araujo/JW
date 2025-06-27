from flask import Flask, jsonify
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

@app.route('/reuniao/<int:ano>/<int:semana>', methods=['GET'])
def get_reuniao(ano, semana):
    url = f'https://wol.jw.org/pt/wol/meetings/r5/lp-t/{ano}/{semana}'
    response = requests.get(url)
    if response.status_code != 200:
        return jsonify({"erro": "Página não encontrada"}), 404

    soup = BeautifulSoup(response.content, 'html.parser')

    # Título - ex: "Semana 27 | Salmo 148"
    titulo = soup.find('h1').get_text(strip=True) if soup.find('h1') else ""
    if " | " in titulo:
        semana_text, capitulo = titulo.split(" | ", 1)
    else:
        semana_text = titulo
        capitulo = ""

    # Função para extrair listas a partir do título da seção
    def get_section_items(title_text):
        header = soup.find(lambda tag: tag.name in ['h3', 'h4'] and title_text in tag.get_text())
        if not header:
            return []
        ul = header.find_next_sibling('ul')
        if not ul:
            return []
        return [li.get_text(strip=True) for li in ul.find_all('li')]

    # Captura seções específicas
    tesouros = get_section_items("Tesouros da Palavra de Deus")
    instrutores = get_section_items("Sejamos Melhores Instrutores")
    vida_crista = get_section_items("Nossa Vida Cristã")

    # Música inicial - normalmente o número aparece em div com classe "opening-song" ou similar
    musica_inicial = ""
    musica_div = soup.find(lambda tag: tag.name == "div" and ("opening-song" in tag.get('class', []) or "song" in tag.get('class', [])))
    if musica_div:
        musica_inicial = musica_div.get_text(strip=True)

    # Música final - similar
    musica_final = ""
    musica_final_div = soup.find(lambda tag: tag.name == "div" and ("concluding-song" in tag.get('class', []) or "final-song" in tag.get('class', [])))
    if musica_final_div:
        musica_final = musica_final_div.get_text(strip=True)

    # Introdução - por padrão na seção inicial, dentro de parágrafo ou div com classe "opening-comments" ou "introduction"
    introducao = ""
    intro_div = soup.find(lambda tag: tag.name == "div" and ("opening-comments" in tag.get('class', []) or "introduction" in tag.get('class', [])))
    if intro_div:
        introducao = intro_div.get_text(strip=True)
    else:
        # fallback: parágrafo logo após título
        titulo_h1 = soup.find('h1')
        if titulo_h1:
            p = titulo_h1.find_next_sibling('p')
            if p:
                introducao = p.get_text(strip=True)

    return jsonify({
        "semana": semana_text,
        "capitulo": capitulo,
        "musica_inicial": musica_inicial,
        "introducao": introducao,
        "tesouros": tesouros,
        "instrutores": instrutores,
        "vida_crista": vida_crista,
        "musica_final": musica_final,
        "url_origem": url
    })

if __name__ == '__main__':
    app.run(debug=True)
