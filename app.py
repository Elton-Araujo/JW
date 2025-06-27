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
    capitulo = capitulo_tag.get_text(strip=True) if capitulo_tag else ""

    # Utilitário para extrair seção com tempos
    def extrair_secao(titulo_secao, incluir_musica=False):
        secao = soup.find(lambda tag: tag.name in ['h2', 'h3'] and titulo_secao.lower() in tag.get_text(strip=True).lower())
        if not secao:
            return []

        itens = []
        for sib in secao.find_all_next():
            if sib.name in ['h2'] and titulo_secao.lower() not in sib.get_text(strip=True).lower():
                break
            if sib.name == 'h3' and sib.get_text(strip=True)[0].isdigit():
                texto = sib.get_text(strip=True)
                itens.append(texto)
            elif incluir_musica and "Cântico" in sib.get_text(strip=True):
                return sib.get_text(strip=True), itens
        return itens if not incluir_musica else ("", itens)

    # Seções com tempo
    tesouros = extrair_secao("Tesouros da Palavra de Deus")
    instrutores = extrair_secao("Sejamos Melhores Instrutores")
    musica_vida_crista, vida_crista = extrair_secao("Nossa Vida Cristã", incluir_musica=True)

    # Músicas (procurando todos os Cânticos)
    canticos = [h3.get_text(strip=True).split("Cântico")[-1].strip() for h3 in soup.find_all('h3') if "Cântico" in h3.get_text()]
    musica_inicial = f"Cântico {canticos[0]}" if len(canticos) > 0 else ""
    musica_final = f"Cântico {canticos[-1]}" if len(canticos) > 1 else musica_inicial
    if not musica_vida_crista and len(canticos) >= 3:
        musica_vida_crista = f"Cântico {canticos[1]}"

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
