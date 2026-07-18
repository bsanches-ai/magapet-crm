from flask import Flask, request, jsonify
from flask_cors import CORS
from escpos.printer import Win32Raw
import datetime

app = Flask(__name__)
CORS(app, origins=["https://bsanches-ai.github.io", "http://localhost", "http://127.0.0.1"])

# Nome da impressora como aparece no Windows (Painel de Controle > Dispositivos e Impressoras)
PRINTER_NAME = "Daruma DR800"

def formatar_linha(texto, largura=42):
    return texto[:largura].ljust(largura)

def separador(char="-", largura=42):
    return char * largura

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"ok": True, "status": "Servidor de impressao ativo"})

@app.route("/print", methods=["POST"])
def imprimir():
    try:
        data = request.json or {}

        pet_nome    = data.get("pet_nome", "—")
        pet_raca    = data.get("pet_raca", "—")
        pet_porte   = data.get("pet_porte", "—")
        pet_pelagem = data.get("pet_pelagem", "—")
        pet_sexo    = data.get("pet_sexo", "")
        tutor_nome  = data.get("tutor_nome", "—")
        servico     = data.get("servico", "—")
        adicionais  = data.get("adicionais", "")
        hora        = data.get("hora", "")
        data_str    = data.get("data", "")

        # Formata data
        try:
            dt = datetime.datetime.strptime(data_str, "%Y-%m-%d")
            data_fmt = dt.strftime("%d/%m/%Y")
        except:
            data_fmt = data_str

        p = Win32Raw(PRINTER_NAME)

        # Cabecalho
        p.set(align="center", bold=True, double_height=True, double_width=True)
        p.text("MagaPet\n")
        p.set(align="center", bold=False, double_height=False, double_width=False)
        p.text("Ficha de Atendimento\n")
        p.text(separador("=") + "\n")

        # Data e hora
        p.set(align="center")
        p.text(f"{data_fmt}  {hora}\n")
        p.text(separador("-") + "\n")

        # Dados do pet
        p.set(align="left", bold=True)
        p.text("PET\n")
        p.set(bold=False)
        sexo_label = " (M)" if pet_sexo == "M" else " (F)" if pet_sexo == "F" else ""
        p.text(f"Nome:    {pet_nome}{sexo_label}\n")
        p.text(f"Raca:    {pet_raca}\n")
        p.text(f"Porte:   {pet_porte}   Pelagem: {pet_pelagem}\n")
        p.text(f"Tutor:   {tutor_nome}\n")
        p.text(separador("-") + "\n")

        # Servico
        p.set(bold=True)
        p.text("SERVICO\n")
        p.set(bold=False)
        p.text(f"{servico}\n")
        if adicionais:
            p.text(f"+ {adicionais}\n")
        p.text(separador("=") + "\n")

        # Desembolo
        p.set(bold=True)
        p.text("Precisou de desembolo?\n")
        p.set(bold=False)
        p.text("\n")
        p.text("  [ ] Sim          [ ] Nao\n")
        p.text("\n")
        p.set(bold=True)
        p.text("Nivel de desembolo:\n")
        p.set(bold=False)
        p.text("\n")
        p.text("  [ ]1  [ ]2  [ ]3  [ ]4  [ ]5\n")
        p.text("\n")
        p.text(separador("-") + "\n")

        # Observacoes
        p.set(bold=True)
        p.text("Observacoes:\n")
        p.set(bold=False)
        p.text("\n")
        p.text("_" * 42 + "\n")
        p.text("\n")
        p.text("_" * 42 + "\n")
        p.text("\n")
        p.text("_" * 42 + "\n")
        p.text("\n")
        p.text(separador("=") + "\n")
        p.text("\n\n")

        p.cut()

        return jsonify({"ok": True})

    except Exception as e:
        return jsonify({"ok": False, "erro": str(e)}), 500


if __name__ == "__main__":
    print("=" * 45)
    print("  Servidor de impressao MagaPet")
    print(f"  Impressora configurada: {PRINTER_NAME}")
    print("  Rodando em http://localhost:5000")
    print("  Mantenha esta janela aberta.")
    print("=" * 45)
    app.run(host="127.0.0.1", port=5000, debug=False)
