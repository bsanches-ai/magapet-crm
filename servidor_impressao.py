from flask import Flask, request, jsonify
from flask_cors import CORS
import datetime

app = Flask(__name__)
CORS(app, origins=["https://bsanches-ai.github.io", "http://localhost", "http://127.0.0.1"])

PORTA    = 'COM3'
LARGURA  = 42

ESC = b'\x1b'
GS  = b'\x1d'

def init():            return ESC + b'@'
def align_center():    return ESC + b'a\x01'
def align_left():      return ESC + b'a\x00'
def bold_on():         return ESC + b'E\x01'
def bold_off():        return ESC + b'E\x00'
def cut():             return GS  + b'V\x00'
def feed(n=3):         return ESC + b'd' + bytes([n])
def txt(s):            return s.encode('cp850', errors='replace')
def linha(s=''):       return txt(s) + b'\n'
def sep(c='-'):        return txt(c * LARGURA) + b'\n'
def central(s):        return txt(s.center(LARGURA)) + b'\n'

def montar_ficha(d):
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

    buf = b''
    buf += linha('==========================================')
    buf += linha('MagaPet')
    buf += linha('Ficha de Atendimento')
    buf += linha(f'{data_fmt}  {hora}')
    buf += linha('==========================================')
    buf += linha(f'Nome:      {pet_nome}')
    buf += linha(f'Raca:      {pet_raca}')
    buf += linha(f'Tutor:     {tutor_nome}')
    buf += linha('------------------------------------------')
    buf += linha('Taxi Dog:  [ ] Sim   [ ] Nao')
    buf += linha('------------------------------------------')
    buf += linha(f'Servico:   {servico}')
    if adicionais:
        buf += linha('Adicionais:')
        for ad in adicionais:
            buf += linha(f'  - {ad}')
    buf += linha('------------------------------------------')
    buf += linha('Desembolo: [ ] Sim   [ ] Nao')
    buf += linha()
    buf += linha('Nivel: [ ]1  [ ]2  [ ]3  [ ]4  [ ]5')
    buf += linha('------------------------------------------')
    buf += linha('Observacao:')
    buf += linha()
    buf += linha('__________________________________________')
    buf += linha()
    buf += linha('__________________________________________')
    buf += linha('==========================================')
    buf += linha()
    buf += linha()
    buf += linha()
    return buf

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
        buf  = montar_ficha(data)
        with open(f'\\\\.\\{PORTA}', 'wb') as porta:
            porta.write(buf)
        return jsonify({'ok': True})
    except Exception as e:
        return jsonify({'ok': False, 'erro': str(e)}), 500

if __name__ == '__main__':
    print('=' * 45)
    print('  Servidor de impressao MagaPet')
    print(f'  Porta: {PORTA}')
    print('  Rodando em http://localhost:5000')
    print('  Mantenha esta janela aberta.')
    print('=' * 45)
    app.run(host='127.0.0.1', port=5000, debug=False)
