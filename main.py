import flet as ft
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import os
from dotenv import load_dotenv

# Carrega as variáveis do arquivo .env
load_dotenv()
folder = os.getenv("FOLDER_ID")

filename = "acesso\plasser-sheet-cfb7c305e34e.json"
scopes = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive",
]

creds = ServiceAccountCredentials.from_json_keyfile_name(filename=filename, scopes=scopes)
client = gspread.authorize(creds)

planilha_completa = client.open(title="maquinas", folder_id=folder)
planilha = planilha_completa.get_worksheet(0)
dados = planilha.get_all_records()




def main(page: ft.Page):
    
    page.scroll = 'auto'
    page.padding = 10
    page.title = "Informações Plasser"

    def capturar(e):
        # 🔥 Envia mensagem para o JavaScript (index.html)
        page.send_message("capturar_compartilhar")

    def limitar(texto, max_chars):
        return texto[:max_chars] + "..." if len(texto) > max_chars else texto

    df = pd.DataFrame(dados)

    icon_status = ft.Icon(ft.Icons.CHECK_CIRCLE, size=22, color=ft.Colors.GREEN)

    def capturar(e):
        page.window.broadcast_event("message", "capturar_compartilhar")

    def home_view():

        #planilha_completa = client.open(title="maquinas", folder_id="15HuBAX0I4xE-xifbuMsYdoseNIEbZORS")
        #planilha = planilha_completa.get_worksheet(0)
        dados = planilha.get_all_records()
        df = pd.DataFrame(dados)

        cards = []

        for index, row  in df.iterrows():
            maq = str(row["maquina"])
            status = str(row["status"])
            if status == "Liberada":
                icon_status = ft.Icon(ft.Icons.CHECK_CIRCLE, size=18, color=ft.Colors.GREEN)
            else:
                icon_status = ft.Icon(ft.Icons.CANCEL, size=18, color=ft.Colors.RED)
            comb = str(row["combustivel"])
            obs = str(row["observacoes"])

            maquina = ft.Container(
                padding=4,
                bgcolor=ft.Colors.GREY_800,
                border_radius=5,
                shadow=ft.BoxShadow(
                    blur_radius=2,
                    spread_radius=1,
                    color=ft.Colors.BLACK12,
                    offset=ft.Offset(0, 2),
                ),
                ink=True,                         # permite clique com efeito ripple
                on_click=lambda e, idx=index: page.go(f"/edit/{idx}"),
                content=ft.ResponsiveRow(
                    controls=[
                        # Coluna 1
                        ft.Container(
                            content=ft.Text(maq, size=12, weight='bold', color=ft.Colors.WHITE),
                            padding=3,
                            col=3,
                        ),

                        # Coluna 2
                        ft.Container(
                            content=ft.Row(
                                [
                                    icon_status,
                                    ft.Text(status, size=12, weight='bold', color=ft.Colors.WHITE),
                                ],
                            ),
                            padding=2,
                            col=6,
                        ),

                        # Coluna 3
                        ft.Container(
                            content=ft.Text(comb , size=14, weight='bold', color=ft.Colors.WHITE),
                            padding=3,
                            col=3,
                        ),

                        ft.Row(
                            [
                                ft.Text(limitar(obs, 50)),
                            ]
                            
                        ),
                    ],
                    spacing=2,
                    run_spacing=2,
                ),
            )
            cards.append(maquina)

            #botao = ft.ElevatedButton(
              #  "Capturar e Compartilhar",
               # icon=ft.Icons.SHARE,
                #on_click=capturar
            #)

            
        return ft.View(
            route="/",
            controls=[
                #ft.Text("Lista de Cards", size=24, weight="bold"),
                *cards,
                #botao
            ]
        )

    # --- 2) Função para montar a view de edição ---
    def edit_view(idx):

        dados = planilha.get_all_records()
        df = pd.DataFrame(dados)
        # pegar dados da linha
        row = df.loc[idx]

        # Criar campos editáveis
        t1 = ft.Text(value=str(row["maquina"]), size=20, weight="bold")

        t2 = ft.RadioGroup(
            value=str(row["status"]),
                content=ft.Column([
                    ft.Radio(value="Liberada", label="Liberada"),
                    ft.Radio(value="Cancelada", label="Cancelada"),
                ]),
        )

        
    # ===== Slider numérico (0 a 100) mostrando '%' no label do próprio Slider =====
    # trata valores como "99%" ou numéricos
        raw = row["combustivel"]
        if isinstance(raw, str) and raw.endswith("%"):
            try:
                valor_inicial = int(raw.replace("%", "").strip())
            except:
                valor_inicial = 0
        else:
            try:
                valor_inicial = int(raw)
            except:
                valor_inicial = 0

        t3_value_text = ft.Text(f"Combustível: {valor_inicial}%", size=12, weight=ft.FontWeight.BOLD)

        t3 = ft.Slider(
            padding=10,
            min=0,
            max=100,
            divisions=20,       # passos de 5 (100/5 = 20)
            value=valor_inicial,
            #label="{value}%",   # mostra 99% automaticamente no slider
            #expand=True,
            on_change=lambda e: (
                setattr(t3_value_text, "value", f"Combustível: {int(e.control.value)}%"),
                page.update()
            ),
        )
        t4 = ft.TextField(label="Observações", value=str(row["observacoes"]), expand=True)

        def salvar(e):
            print(idx, t1.value, t2.value, int(t3.value), t4.value)
            
            planilha.update_acell(label= f"A{idx + 2}", value=t1.value)
            planilha.update_acell(label= f"B{idx + 2}", value=t2.value)
            planilha.update_acell(label= f"C{idx + 2}", value=str(int(t3.value)) + "%")
            planilha.update_acell(label= f"D{idx + 2}", value=t4.value)

            #df.to_excel("dados.xlsx", index=False)  # salvar na planilha

            page.go("/")  # voltar para home

        return ft.View(
            route=f"/edit/{idx}",
            controls=[
                #ft.Text(f"Editando linha {idx}", size=20, weight="bold"),
                t1, t2, t3_value_text, t3, t4,
                ft.Row(
                    [
                        ft.ElevatedButton("Salvar", icon=ft.Icons.SAVE, on_click=salvar),
                        ft.TextButton("Cancelar", on_click=lambda _: page.go("/")),
                    ]
                )
                
            ],
            vertical_alignment="start",
            spacing=15,
            padding=20,
        )

    # --- 3) Controle de rotas ---
    def route_change(e):
        page.views.clear()

        route = page.route

        if route == "/":
            page.views.append(home_view())

        elif route.startswith("/edit/"):
            idx = int(route.split("/")[-1])
            page.views.append(edit_view(idx))

        page.update()

    page.on_route_change = route_change
    page.go("/")

    


if __name__ == '__main__':
    ft.app(
        target=main,
        assets_dir='assets'
    )