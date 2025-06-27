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

    # Função para extrair seção com títulos e tempos
    def extrair_secao(titulo_secao, incluir_musica=False):
        secao_titulo = soup.find(lambda tag: tag.name in ['h2', 'h3'] and titulo_secao.lower() in tag.get_text(strip=True).lower())
        if not secao_titulo:
            return "" if incluir_musica else []

        itens = []
        musica = ""

        next_el = secao_titulo.find_next_sibling()
        while next_el:
            if next_el.name == 'h2':
                break
            if next_el.name == 'h3':
                texto = next_el.get_text(strip=True)
                if "Cântico" in texto and incluir_musica:
                    musica = texto
                elif texto[0].isdigit():
                    # tenta encontrar o tempo
                    tempo_tag = next_el.find_next_sibling()
                    tempo = ""
                    if tempo_tag and tempo_tag.name == "div":
                        p_tag = tempo_tag.find("p")
                        if p_tag:
                            tempo = p_tag.get_text(strip=True)
                    if tempo:
                        texto = f"{texto} ({tempo})"
                    itens.append(texto)
            next_el = next_el.find_next_sibling()

        return (musica, itens) if incluir_musica else itens

    # Seções
    tesouros = extrair_secao("Tesouros da Palavra de Deus")
    instrutores = extrair_secao("Sejamos Melhores Instrutores")
    musica_vida_crista, vida_crista = extrair_secao("Nossa Vida Cristã", incluir_musica=True)

    # Limpeza das músicas
    def extrair_cantico(texto):
        if "Cântico" not in texto:
            return ""
        partes = texto.split("Cântico")
        numero = partes[-1].split()[0]
        return f"Cântico {numero}"

    canticos = [extrair_cantico(h3.get_text(strip=True)) for h3 in soup.find_all('h3') if "Cântico" in h3.get_text()]
    musica_inicial = canticos[0] if len(canticos) > 0 else ""
    musica_final = canticos[-1] if len(canticos) > 1 else ""

    return jsonify({
        "semana": semana_text,
        "capitulo": capitulo,
        "musica_inicial": musica_inicial,
        "musica_vida_crista": extrair_cantico(musica_vida_crista),
        "musica_final": musica_final,
        "tesouros": tesouros,
        "instrutores": instrutores,
        "vida_crista": vida_crista,
        "url_origem": url
    })

if __name__ == '__main__':
    app.run(debug=True)
