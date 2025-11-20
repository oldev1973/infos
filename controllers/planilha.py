import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials

filename = "acesso\plasser-sheet-cfb7c305e34e.json"
scopes = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive",
]

creds = ServiceAccountCredentials.from_json_keyfile_name(filename=filename, scopes=scopes)
client = gspread.authorize(creds)
print(client)

planilha_completa = client.open(title="maquinas", folder_id="15HuBAX0I4xE-xifbuMsYdoseNIEbZORS")
planilha = planilha_completa.get_worksheet(0)
dados = planilha.get_all_records()
df = pd.DataFrame(dados)

def mostrar_planilha(planilha):
    dados = planilha.get_all_records()
    df = pd.DataFrame(dados)
    print(df)

if __name__ == '__main__':

    #READ
    mostrar_planilha(planilha)


    #CREATE / UPDATE
    planilha.update_acell(label="A12", value="ETS1")
    mostrar_planilha(planilha)

    #DELETE
    #planilha.delete_rows(11)
    #mostrar_planilha(planilha)