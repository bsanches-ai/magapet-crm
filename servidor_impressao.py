from flask import Flask, request, jsonify
from flask_cors import CORS
import win32print
import datetime

app = Flask(__name__)
CORS(app, origins=["https://bsanches-ai.github.io", "http://localhost", "http://127.0.0.1"])

PRINTER_NAME = "Daruma DR800"

ESC = b'\x1b'
GS  = b'\x1d'

def init():         return ESC + b'@'
def align(a):       return ESC + b'a' + (b'\x01' if a=='center' else b'\x02' if a=='right' else b'\x00')
def bold(on):       return ESC + b'E' + (b'\x01' if on else b'\x00')
def double(on):     return GS  + b'!' + (b'\x11' if on else b'\x00')
def cut():          return GS  + b'V\x00'
def txt(s):         return s.encode('cp850', errors='replace')
def line(s=''):     return txt(s) + b'\n'
def sep(c='-', n=42): return txt(c * n) + b'\n'

def montar_ficha(d):
    pet_nome    = d.get('pet_nome', '-')
    pet_raca    = d.get('pet_raca', '-')
    pet_porte   = d.get('pet_porte', '-')
    pet_pelagem = d.get('pet_pelagem', '-')
    pet_sexo    = d.get('pet_sexo', '')
    tutor_nome  = d.get('tutor_nome', '-')
    servico     = d.get('servico', '-')
    adicionais  = d.get('adicionais', '')
    hora        = d.get('hora', '')
    data_str    = d.get('data', '')
    try:
        dt = datetime.datetime.strptime(data_str, '%Y-%m-%d')
        data_fmt = dt.strftime('%d/%m/%Y')
    except:
        data_fmt = data_str
    sexo_label = ' (M)' if pet_sexo == 'M' else ' (F)' if pet_sexo == 'F' else ''

    buf = b''
    buf += init()
    buf += align('center') + double(True) + bold(True)
    buf += line('MagaPet')
    buf += double(False) + bold(False)
    buf += line('Ficha de Atendimento')
    buf += sep('=')
    buf += line(f'{data_fmt}  {hora}')
    buf += sep('-')
    buf += align('left') + bold(True) + line('PET')
    buf += bold(False)
    buf += line(f'Nome:    {pet_nome}{sexo_label}')
    buf += line(f'Raca:    {pet_raca}')
    buf += line(f'Porte:   {pet_porte}   Pelagem: {pet_pelagem}')
    buf += line(f'Tutor:   {tutor_nome}')
    buf += sep('-')
    buf += bold(True) + line('SERVICO') + bold(False)
    buf += line(servico)
    if adicionais:
        buf += line(f'+ {adicionais}')
    buf += sep('=')
    buf += bold(True) + line('Precisou de desembolo?') + bold(False)
    buf += line()
    buf += line('  [ ] Sim          [ ] Nao')
    buf += line()
    buf += bold(True) + line('Nivel de desembolo:') + bold(False)
    buf += line()
    buf += line('  [ ]1  [ ]2  [ ]3  [ ]4  [ ]5')
    buf += line()
    buf += sep('-')
    buf += bold(True) + line('Observacoes:') + bold(False)
    buf += line()
    buf += line('_' * 42)
    buf += line()
    buf += line('_' * 42)
    buf += line()
    buf += line('_' * 42)
    buf += line()
    buf += sep('=')
    buf += b'\n\n\n'
    buf += cut()
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
            win32print.StartDocPrinter(hPrinter, 1, ('MagaPet Ficha', None, 'RAW'))
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
