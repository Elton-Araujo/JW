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

    # Semana e Capítulo
    semana_text = soup.find('h1').get_text(strip=True) if soup.find('h1') else ""
    capitulo_tag = soup.find('h2')
    capitulo = capitulo_tag.get_text(strip=True).replace(" |", "") if capitulo_tag else ""

    # Função auxiliar para buscar tempo
    def buscar_tempo(elem):
        next_div = elem.find_next_sibling("div")
        if next_div:
            tempo_p = next_div.find("p")
            if tempo_p and "(" in tempo_p.text:
                return tempo_p.text.strip()
        return ""

    # Extrair itens de seção
    def extrair_secao(nome, incluir_musica=False):
        inicio = soup.find(lambda tag: tag.name == "h2" and nome.lower() in tag.text.lower())
        if not inicio:
            return ("", []) if incluir_musica else []
        
        elementos = []
        musica = ""

        for tag in inicio.find_all_next():
            if tag.name == "h2" and tag.text.strip() != inicio.text.strip():
                break  # fim da seção

            if incluir_musica and tag.name == "h3" and "Cântico" in tag.text:
                musica = tag.text.strip().split("e")[0].strip()
            
            if tag.name == "h3" and tag.text.strip()[0].isdigit():
                tempo = buscar_tempo(tag)
                texto = f"{tag.text.strip()} ({tempo})" if tempo else tag.text.strip()
                elementos.append(texto)

        return (musica, elementos) if incluir_musica else elementos

    # Cânticos
    canticos = [h3.get_text(strip=True).split("e")[0].strip()
                for h3 in soup.find_all("h3") if "Cântico" in h3.get_text()]
    musica_inicial = canticos[0] if len(canticos) > 0 else ""
    musica_final = canticos[-1] if len(canticos) > 1 else ""

    # Seções
    tesouros = extrair_secao("Tesouros da Palavra de Deus")
    instrutores = extrair_secao("Sejamos Melhores Instrutores")
    musica_vida_crista, vida_crista = extrair_secao("Nossa Vida Cristã", incluir_musica=True)

    return jsonify({
        "semana": semana_text,
        "capitulo": capitulo,
        "musica_inicial": musica_inicial,
        "musica_vida_crista": musica_vida_crista,
        "musica_final": musica_final,
        "tesouros": tesouros,
        "instrutores": instrutores,
        "vida_crista": vida_crista,
        "url_origem": url
    })

if __name__ == '__main__':
    app.run(debug=True)
