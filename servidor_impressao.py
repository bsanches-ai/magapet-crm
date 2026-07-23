from flask import Flask, request, jsonify
from flask_cors import CORS
import win32print
import datetime

app = Flask(__name__)
CORS(app, origins=["https://bsanches-ai.github.io", "http://localhost", "http://127.0.0.1"])

PRINTER_NAME = "Daruma DR800"
LARGURA = 42

def linha(texto=''):
    return (texto + '\r\n').encode('cp850', errors='replace')

def sep(c='-'):
    return linha(c * LARGURA)

def centralizar(texto):
    return linha(texto.center(LARGURA))

def montar_ficha(d):
    pet_nome   = d.get('pet_nome', '-')
    pet_raca   = d.get('pet_raca', '-')
    tutor_nome = d.get('tutor_nome', '-')
    taxi_dog   = d.get('taxi_dog', False)
    servico    = d.get('servico', '-')
    adicionais = d.get('adicionais', [])
    if isinstance(adicionais, str):
        adicionais = [a.strip() for a in adicionais.split(',') if a.strip()]
    # Se o serviço é tosa, banho já está incluso — remove dos adicionais
    if 'tosa' in servico.lower():
        adicionais = [a for a in adicionais if 'banho' not in a.lower()]
    hora       = d.get('hora', '')
    data_str   = d.get('data', '')
    try:
        dt = datetime.datetime.strptime(data_str, '%Y-%m-%d')
        data_fmt = dt.strftime('%d/%m/%Y')
    except:
        data_fmt = data_str

    taxi_sim = '[ ]'
    taxi_nao = '[ ]'

    buf = b''
    buf += sep('=')
    buf += centralizar('MagaPet')
    buf += centralizar('Ficha de Atendimento')
    buf += centralizar(f'{data_fmt}  {hora}')
    buf += sep('=')
    buf += linha(f'Nome:      {pet_nome}')
    buf += linha(f'Raca:      {pet_raca}')
    buf += linha(f'Tutor:     {tutor_nome}')
    buf += sep('-')
    buf += linha(f'Taxi Dog:  {taxi_sim} Sim   {taxi_nao} Nao')
    buf += sep('-')
    buf += linha(f'Servico:   {servico}')
    if adicionais:
        buf += linha('Adicionais:')
        for ad in adicionais:
            buf += linha(f'  - {ad}')
    buf += sep('-')
    buf += linha('Desembolo: [ ] Sim   [ ] Nao')
    buf += linha()
    buf += linha('Nivel: [ ]1  [ ]2  [ ]3  [ ]4  [ ]5')
    buf += sep('-')
    buf += linha('Observacao:')
    buf += linha()
    buf += linha('_' * LARGURA)
    buf += linha()
    buf += linha('_' * LARGURA)
    buf += sep('=')
    buf += linha()
    buf += linha()
    buf += linha()
    return buf

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'ok': True, 'status': 'Servidor de impressao ativo'})

@app.route('/print', methods=['POST'])
def imprimir():
    try:
        data = request.json or {}
        buf = montar_ficha(data)
        hPrinter = win32print.OpenPrinter(PRINTER_NAME)
        try:
            win32print.StartDocPrinter(hPrinter, 1, ('MagaPet Ficha', None, 'TEXT'))
            win32print.StartPagePrinter(hPrinter)
            win32print.WritePrinter(hPrinter, buf)
            win32print.EndPagePrinter(hPrinter)
            win32print.EndDocPrinter(hPrinter)
        finally:
            win32print.ClosePrinter(hPrinter)
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
