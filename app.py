from flask import Flask, jsonify
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

@app.route('/reuniao/<int:ano>/<int:semana>', methods=['GET'])
def get_reuniao(ano, semana):
    url = f'https://wol.jw.org/pt/wol/meetings/r5/lp-t/{ano}/{semana}'
    resp = requests.get(url)
    if resp.status_code != 200:
        return jsonify({"erro": "Página não encontrada"}), 404

    soup = BeautifulSoup(resp.content, 'html.parser')

    # Semana (h1) e Capítulo (h2 logo após)
    semana_text = soup.find('h1').get_text(strip=True) if soup.find('h1') else ""
    capitulo_tag = soup.find('h2')
    capitulo = capitulo_tag.get_text(strip=True) if capitulo_tag else ""

    # Função para extrair tópicos de cada seção, baseando-se nos h3 numerados após h2/h3 com título
    def extrair_secao(titulo_secao):
        secao = soup.find(lambda tag: tag.name in ['h2', 'h3'] and titulo_secao.lower() in tag.get_text(strip=True).lower())
        if not secao:
            return []

        itens = []
        for sib in secao.find_all_next():
            if sib.name in ['h2'] and titulo_secao.lower() not in sib.get_text(strip=True).lower():
                break
            if sib.name == 'h3' and sib.get_text(strip=True)[0].isdigit():
                itens.append(sib.get_text(strip=True))
        return itens

    # Extraindo listas das seções
    tesouros = extrair_secao("Tesouros da Palavra de Deus")
    instrutores = extrair_secao("Sejamos Melhores Instrutores")
    vida_crista = extrair_secao("Nossa Vida Cristã")

    # Músicas — h3 com "Cântico"
    canticos = [h3.get_text(strip=True).split('Cântico')[-1].strip() for h3 in soup.find_all('h3') if "Cântico" in h3.get_text()]
    musica_inicial = f"Cântico {canticos[0]}" if canticos else ""
    musica_final = f"Cântico {canticos[-1]}" if len(canticos) > 1 else musica_inicial

    # Introdução — opcional (não visível claramente na estrutura atual)
    introducao = ""

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
