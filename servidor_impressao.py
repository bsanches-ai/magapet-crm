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
    buf += sep('=')
    buf += centralizar('MagaPet')
    buf += centralizar('Ficha de Atendimento')
    buf += sep('=')
    buf += centralizar(f'{data_fmt}  {hora}')
    buf += sep('-')
    buf += linha('PET')
    buf += linha(f'Nome:    {pet_nome}{sexo_label}')
    buf += linha(f'Raca:    {pet_raca}')
    buf += linha(f'Porte:   {pet_porte}   Pelagem: {pet_pelagem}')
    buf += linha(f'Tutor:   {tutor_nome}')
    buf += sep('-')
    buf += linha('SERVICO')
    buf += linha(servico)
    if adicionais:
        buf += linha(f'+ {adicionais}')
    buf += sep('=')
    buf += linha('Precisou de desembolo?')
    buf += linha()
    buf += linha('  [ ] Sim          [ ] Nao')
    buf += linha()
    buf += linha('Nivel de desembolo:')
    buf += linha()
    buf += linha('  [ ]1  [ ]2  [ ]3  [ ]4  [ ]5')
    buf += linha()
    buf += sep('-')
    buf += linha('Observacoes:')
    buf += linha()
    buf += linha('_' * LARGURA)
    buf += linha()
    buf += linha('_' * LARGURA)
    buf += linha()
    buf += linha('_' * LARGURA)
    buf += linha()
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
