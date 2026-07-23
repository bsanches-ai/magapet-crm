from flask import Flask, request, jsonify
from flask_cors import CORS
import win32ui
import win32con
import datetime

app = Flask(__name__)
CORS(app, origins=["https://bsanches-ai.github.io", "http://localhost", "http://127.0.0.1"])

PRINTER_NAME = "Daruma DR800"

def montar_linhas(d):
    pet_nome   = d.get('pet_nome', '-')
    pet_raca   = d.get('pet_raca', '-')
    tutor_nome = d.get('tutor_nome', '-')
    servico    = d.get('servico', '-')
    adicionais = d.get('adicionais', [])
    hora       = d.get('hora', '')
    data_str   = d.get('data', '')

    if isinstance(adicionais, str):
        adicionais = [a.strip() for a in adicionais.split(',') if a.strip()]
    if 'tosa' in servico.lower():
        adicionais = [a for a in adicionais if 'banho' not in a.lower()]

    try:
        dt = datetime.datetime.strptime(data_str, '%Y-%m-%d')
        data_fmt = dt.strftime('%d/%m/%Y')
    except:
        data_fmt = data_str

    SEP  = '-' * 42
    SEP2 = '=' * 42

    linhas = []
    linhas.append(SEP2)
    linhas.append('             MagaPet')
    linhas.append('       Ficha de Atendimento')
    linhas.append(f'       {data_fmt}  {hora}')
    linhas.append(SEP2)
    linhas.append(f'Nome:      {pet_nome}')
    linhas.append(f'Raca:      {pet_raca}')
    linhas.append(f'Tutor:     {tutor_nome}')
    linhas.append(SEP)
    linhas.append('Taxi Dog:  [ ] Sim   [ ] Nao')
    linhas.append(SEP)
    linhas.append(f'Servico:   {servico}')
    if adicionais:
        linhas.append('Adicionais:')
        for ad in adicionais:
            linhas.append(f'  - {ad}')
    linhas.append(SEP)
    linhas.append('Desembolo: [ ] Sim   [ ] Nao')
    linhas.append('')
    linhas.append('Nivel: [ ]1  [ ]2  [ ]3  [ ]4  [ ]5')
    linhas.append(SEP)
    linhas.append('Observacao:')
    linhas.append('')
    linhas.append('_' * 42)
    linhas.append('')
    linhas.append('_' * 42)
    linhas.append(SEP2)
    return linhas

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'ok': True, 'status': 'Servidor de impressao ativo'})

@app.route('/print', methods=['POST'])
def imprimir():
    try:
        data  = request.json or {}
        linhas = montar_linhas(data)

        dc = win32ui.CreateDC()
        dc.CreatePrinterDC(PRINTER_NAME)

        # Tamanho do papel em pixels (DPI da impressora)
        dpi_x = dc.GetDeviceCaps(win32con.LOGPIXELSX)
        altura_fonte = max(14, dpi_x // 15)  # ~14pt adaptado ao DPI

        fonte = win32ui.CreateFont({
            'name':   'Courier New',
            'height': altura_fonte,
            'weight': 400,
            'charset': 0,
        })
        dc.SelectObject(fonte)

        margem_x = dpi_x // 10
        espaco_y = int(altura_fonte * 1.4)
        y = dpi_x // 10

        dc.StartDoc('MagaPet Ficha')
        dc.StartPage()

        for linha in linhas:
            dc.TextOut(margem_x, y, linha)
            y += espaco_y

        dc.EndPage()
        dc.EndDoc()
        dc.DeleteDC()

        return jsonify({'ok': True})
    except Exception as e:
        return jsonify({'ok': False, 'erro': str(e)}), 500

if __name__ == '__main__':
    print('=' * 45)
    print('  Servidor de impressao MagaPet')
    print(f'  Impressora: {PRINTER_NAME}')
    print('  Rodando em http://localhost:5000')
    print('  Mantenha esta janela aberta.')
    print('=' * 45)
    app.run(host='127.0.0.1', port=5000, debug=False)
