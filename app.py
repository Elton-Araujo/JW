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

    # Cânticos iniciais e finais
    musicas = soup.find_all('h3')
    musica_inicial = ""
    musica_final = ""
    musica_vida_crista = ""

    for h3 in musicas:
        texto = h3.get_text(strip=True)
        if "Comentários iniciais" in texto:
            musica_inicial = texto.split("e")[0].strip()
        elif "Comentários finais" in texto:
            musica_final = texto.split("e")[0].strip()
        elif "Vida Cristã" in h3.find_previous("h2").text:
            if "Cântico" in texto:
                musica_vida_crista = texto.split("e")[0].strip()

    # Função para buscar itens com tempo
    def extrair_itens(inicio_tag):
        itens = []
        for tag in inicio_tag.find_all_next():
            if tag.name == "h2":
                break  # fim da seção
            if tag.name == "h3" and tag.text.strip()[0].isdigit():
                titulo = tag.text.strip()
                tempo = ""
                next_div = tag.find_next_sibling("div")
                if next_div:
                    tempo_p = next_div.find("p")
                    if tempo_p:
                        tempo = tempo_p.text.strip()
                if tempo:
                    titulo += f" ({tempo})"
                itens.append(titulo)
        return itens

    # Tesouros da Palavra de Deus
    secao_tesouros = soup.find("h2", string=lambda text: text and "TESOUROS DA PALAVRA DE DEUS" in text.upper())
    tesouros = extrair_itens(secao_tesouros) if secao_tesouros else []

    # Sejamos Melhores Instrutores
    secao_instrutores = soup.find("h2", string=lambda text: text and "FAÇA SEU MELHOR NO MINISTÉRIO" in text.upper())
    instrutores = extrair_itens(secao_instrutores) if secao_instrutores else []

    # Nossa Vida Cristã
    secao_vida = soup.find("h2", string=lambda text: text and "NOSSA VIDA CRISTÃ" in text.upper())
    vida_crista = extrair_itens(secao_vida) if secao_vida else []

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
