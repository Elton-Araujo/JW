from flask import Flask, jsonify
import requests
from bs4 import BeautifulSoup, NavigableString

app = Flask(__name__)

@app.route('/reuniao/<int:ano>/<int:semana>', methods=['GET'])
def get_reuniao(ano, semana):
    url = f'https://wol.jw.org/pt/wol/meetings/r5/lp-t/{ano}/{semana}'
    resp = requests.get(url)
    if resp.status_code != 200:
        return jsonify({"erro": "Página não encontrada"}), 404

    soup = BeautifulSoup(resp.content, 'html.parser')

    # Semana e Capítulo
    semana_text = soup.find('h1').get_text(strip=True) if soup.find('h1') else ""
    capitulo_tag = soup.find('h2')
    capitulo = capitulo_tag.get_text(strip=True) if capitulo_tag else ""

    # Função para pegar uma seção pelo título (ex: "TESOUROS DA PALAVRA DE DEUS")
    # e retornar lista dos títulos dos subtópicos (<h3>) nessa seção
    def extrair_secao(titulo_secao):
        secao = soup.find('h2', string=lambda text: text and titulo_secao.lower() in text.lower())
        if not secao:
            return []

        itens = []
        # Percorre os irmãos após esse h2, até encontrar outro h2 (nova seção) ou fim
        for sib in secao.find_next_siblings():
            if sib.name == 'h2':
                break
            if sib.name == 'h3':
                texto = sib.get_text(strip=True)
                if texto:
                    itens.append(texto)
        return itens

    tesouros = extrair_secao("Tesouros da Palavra de Deus")
    instrutores = extrair_secao("Sejamos Melhores Instrutores")
    vida_crista = extrair_secao("Nossa Vida Cristã")

    # Capturar músicas: todos os h3 que têm "Cântico" no texto
    canticos = [h3.get_text(strip=True) for h3 in soup.find_all('h3') if "Cântico" in h3.get_text()]

    musica_inicial = canticos[0] if canticos else ""
    musica_final = canticos[-1] if len(canticos) > 1 else musica_inicial

    # Capturar introdução: parágrafos logo após o h1 e h2, antes da primeira seção (h2)
    introducao = ""
    h1 = soup.find('h1')
    if h1:
        next_node = h1.find_next_sibling()
        textos_intro = []
        while next_node and next_node.name != 'h2':
            if next_node.name == 'p':
                textos_intro.append(next_node.get_text(strip=True))
            next_node = next_node.find_next_sibling()
        introducao = " ".join(textos_intro)

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
