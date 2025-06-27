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
    capitulo_tag = soup.select_one("h2")
    capitulo = capitulo_tag.get_text(strip=True).replace("PROVÉRBIOS ", "PROVÉRBIOS ") if capitulo_tag else ""

    musica_inicial_tag = soup.find("h3", string=lambda x: x and "Comentários iniciais" in x)
    musica_inicial = musica_inicial_tag.get_text(strip=True).split("e oração")[0].strip() if musica_inicial_tag else ""

    musica_final_tag = soup.find("h3", string=lambda x: x and "Comentários finais" in x)
    musica_final = "Cântico 150" if musica_final_tag else ""

    musica_vida_crista_tag = soup.find("h3", string=lambda x: x and "Cântico 78" in x)
    musica_vida_crista = "Cântico 78" if musica_vida_crista_tag else ""

    def extract_lista(base_id, prefix):
        lista = []
        h3_tags = soup.select(f"h3:has(strong):contains('{prefix}')")
        for h3 in h3_tags:
            idx = h3.find_previous("h2")
            if idx:
                break

        section = h3.find_parent("div") if h3 else None
        if not section:
            return lista

        count = 1
        for tag in section.find_all("h3"):
            text = tag.get_text(" ", strip=True)
            if not text:
                continue

            time_tag = tag.find_next("p")
            tempo = ""
            if time_tag and "min" in time_tag.text:
                tempo = time_tag.text.strip().replace("(", "").replace(")", "")

            item = f"{count}. {text.split('(')[0].strip()} ({tempo})" if tempo else f"{count}. {text.split('(')[0].strip()}"
            lista.append(item)
            count += 1

        return lista

    def extract_itens_from_h3_and_time(start_h3_str, count=3):
        blocos = []
        h3s = soup.find_all("h3")
        for h3 in h3s:
            if start_h3_str in h3.text:
                atual = h3
                for i in range(count):
                    if not atual:
                        break
                    titulo = atual.get_text(" ", strip=True)
                    p = atual.find_next("p")
                    tempo = ""
                    if p and "min" in p.text:
                        tempo = p.text.strip().replace("(", "").replace(")", "")

                    nome = titulo.split("((", 1)[0].strip()
                    item = f"{nome} ({tempo})" if tempo else nome
                    blocos.append(item)
                    atual = atual.find_next("h3")
                break
        return blocos

    def extract_itens_by_range(start, end):
        result = []
        for i in range(start, end + 1):
            label = soup.find("h3", string=lambda x: x and x.strip().startswith(f"{i}.") )
            if not label:
                continue
            text = label.get_text(" ", strip=True)
            tempo_tag = label.find_next("p")
            tempo = ""
            if tempo_tag and "min" in tempo_tag.text:
                tempo = tempo_tag.text.strip().replace("(", "").replace(")", "")
            result.append(f"{text.split('(')[0].strip()} ({tempo})")
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
