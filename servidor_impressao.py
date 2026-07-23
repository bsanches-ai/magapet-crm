from flask import Flask, request, jsonify
from flask_cors import CORS
import win32ui
import win32con
import win32print
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
    except Exception:
        data_fmt = data_str

    L = 42
    linhas = [
        '=' * L,
        '        MagaPet',
        '   Ficha de Atendimento',
        f'   {data_fmt}  {hora}',
        '=' * L,
        f'Nome:      {pet_nome}',
        f'Raca:      {pet_raca}',
        f'Tutor:     {tutor_nome}',
        '-' * L,
        'Taxi Dog:  [ ] Sim   [ ] Nao',
        '-' * L,
        f'Servico:   {servico}',
    ]
    if adicionais:
        linhas.append('Adicionais:')
        for ad in adicionais:
            linhas.append(f'  - {ad}')
    linhas += [
        '-' * L,
        'Desembolo: [ ] Sim   [ ] Nao',
        '',
        'Nivel: [ ]1  [ ]2  [ ]3  [ ]4  [ ]5',
        '-' * L,
        'Observacao:',
        '',
        '_' * L,
        '',
        '_' * L,
        '=' * L,
        '',
        '',
        '',
    ]
    return linhas

def imprimir_gdi(linhas):
    dc = win32ui.CreateDC()
    dc.CreatePrinterDC(PRINTER_NAME)
    dc.StartDoc("MagaPet Ficha")
    dc.StartPage()

    dpi_x = dc.GetDeviceCaps(win32con.LOGPIXELSX)
    dpi_y = dc.GetDeviceCaps(win32con.LOGPIXELSY)

    # Fonte monoespaçada 9pt (negativo = tamanho em pontos lógicos)
    altura_fonte = -int(dpi_y * 9 / 72)
    fonte = win32ui.CreateFont({
        'name': 'Courier New',
        'height': altura_fonte,
        'weight': win32con.FW_NORMAL,
        'charset': win32con.ANSI_CHARSET,
    })
    fonte_antiga = dc.SelectObject(fonte)

    tm = dc.GetTextMetrics()
    altura_linha = tm['tmHeight'] + tm['tmExternalLeading'] + 2

    x = int(dpi_x * 0.03)
    y = int(dpi_y * 0.05)

    for linha in linhas:
        dc.TextOut(x, y, linha if linha else ' ')
        y += altura_linha

    dc.SelectObject(fonte_antiga)
    dc.EndPage()
    dc.EndDoc()
    dc.DeleteDC()

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'ok': True, 'status': 'Servidor ativo'})

@app.route('/print', methods=['POST'])
def imprimir():
    try:
        data = request.json or {}
        print('=== DADOS RECEBIDOS ===')
        print(f"pet_nome:   {data.get('pet_nome')}")
        print(f"pet_raca:   {data.get('pet_raca')}")
        print(f"tutor_nome: {data.get('tutor_nome')}")
        print(f"servico:    {data.get('servico')}")
        print(f"adicionais: {data.get('adicionais')}")
        print(f"hora:       {data.get('hora')}")
        print(f"data:       {data.get('data')}")
        print('=======================')
        linhas = montar_linhas(data)
        imprimir_gdi(linhas)
        print('[OK] Ficha impressa via GDI')
        return jsonify({'ok': True})
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'ok': False, 'erro': str(e)}), 500

if __name__ == '__main__':
    print('=' * 45)
    print('  Servidor de impressao MagaPet')
    print(f'  Impressora: {PRINTER_NAME}')
    print('  Rodando em http://localhost:5000')
    print('  Mantenha esta janela aberta.')
    print('=' * 45)
    app.run(host='127.0.0.1', port=5000, debug=False)
