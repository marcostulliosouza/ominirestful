import requests
import time
import os
import json
import sys
import pandas as pd

BASE_URL = "https://omnifrota.omnilink.com.br"
LOGIN_URL = f"{BASE_URL}/api/authapi/login"
QUERY_URL_FULL = f"{BASE_URL}/api/ApiTesteChip6450/gettestechips6450"

payload = {
    "Username": "hi-mix",
    "Password": "HI.omni@123"
}

TOKEN_FILE = "C:/eXTP/token.json"


def get_excel_path():
    """Obtém o caminho absoluto para o arquivo Excel na mesma pasta do executável"""
    if getattr(sys, 'frozen', False):
        # Se estiver rodando como executável
        base_path = os.path.dirname(sys.executable)
    else:
        # Se estiver rodando como script
        base_path = os.path.dirname(os.path.abspath(__file__))

    return os.path.join(base_path, "Simcards Algar -Vivo.xlsx")


def save_token(token, expires_at):
    with open(TOKEN_FILE, 'w') as f:
        json.dump({"token": token, "expires_at": expires_at}, f)


def load_token():
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, 'r') as f:
            return json.load(f)
    return None


def fazer_login():
    try:
        response = requests.post(LOGIN_URL, json=payload)
        response.raise_for_status()
        token = response.json().get("token")
        expires_in = 30 * 24 * 60 * 60
        expires_at = time.time() + expires_in
        return token, expires_at
    except requests.exceptions.RequestException as e:
        return None, None


def get_token():
    token_info = load_token()
    if token_info is None or time.time() >= token_info["expires_at"]:
        token, expires_at = fazer_login()
        if token:
            save_token(token, expires_at)
            return token
        else:
            raise Exception("Falha ao obter novo token")
    return token_info["token"]


def fazer_consulta(iccid):
    try:
        token = get_token()
        headers = {"Authorization": f"Bearer {token}"}
        params = {"iccid": iccid}

        response = requests.get(QUERY_URL_FULL, headers=headers, params=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return None


def consultar_excel(iccid):
    try:
        excel_path = get_excel_path()
        if not os.path.exists(excel_path):
            print(f"Arquivo Excel não encontrado em: {excel_path}")
            return None

        df = pd.read_excel(excel_path, dtype={'ICCID': str, 'MSISDN': str}, engine='openpyxl')
        linha = df[df['ICCID'] == iccid]

        if not linha.empty:
            return linha.iloc[0]['MSISDN']
        return None
    except Exception as e:
        print(f"Erro ao ler arquivo Excel: {str(e)}")
        return None


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(1)

    iccid = sys.argv[1].strip()

    if iccid.startswith('895532'):
        msisdn = consultar_excel(iccid)
        if msisdn:
            print(msisdn)
        else:
            print("Nenhum resultado encontrado no arquivo Excel.")
    else:
        resultado = fazer_consulta(iccid)
        if resultado:
            print(resultado[0]['callingStationID'])
        else:
            print("Nenhum resultado encontrado ou erro na consulta.")