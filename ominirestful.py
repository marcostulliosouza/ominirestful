import requests
import time
import os
import json
import sys  # Adicionado para capturar argumentos da linha de comando

BASE_URL = "https://omnifrota.omnilink.com.br"
LOGIN_URL = f"{BASE_URL}/api/authapi/login"
QUERY_URL_FULL = f"{BASE_URL}/api/ApiTesteChip6450/gettestechips6450"

payload = {
    "Username": "hi-mix",
    "Password": "HI.omni@123"
}

TOKEN_FILE = "C:/eXTP/token.json"


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
        expires_in = 30 * 24 * 60 * 60  # 30 dias em segundos
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


if __name__ == "__main__":
    # Verifica se o ICCID foi passado como argumento
    if len(sys.argv) != 2:
        sys.exit(1)  # Encerra o programa com código de erro

    iccid = sys.argv[1].strip()  # Captura o ICCID do primeiro argumento
    resultado = fazer_consulta(iccid)
    if resultado:
        print(resultado[0]['callingStationID'])
    else:
        print("Nenhum resultado encontrado ou erro na consulta.")
