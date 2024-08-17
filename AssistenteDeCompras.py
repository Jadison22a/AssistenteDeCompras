import tkinter
import customtkinter as ctk
from datetime import datetime
import mysql.connector
import plotly.express as px
import pandas as pd
from PIL import Image, ImageTk
import os
import subprocess   #exclusivo para o linux pois o mesmo não consegue remover arquivos com a biblioteca 'os'
import platform

# ============================================configuraçoes da janela CTK===============================================
# Configurações da janela
janela = ctk.CTk()
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")

# Obtendo a largura e altura da tela
screen_width = janela.winfo_screenwidth()
screen_height = janela.winfo_screenheight()

# Definindo a geometria da janela para ocupar a tela toda
janela.geometry(f"{screen_width}x{screen_height}")

# Lista global para armazenar referências dos botões de cotação e as checkbox
botoes_cotacoes = []
checkboxGlobal = []
botao_deletarCotacao = []

# ==========================================configurações Banco de dados================================================
if platform.system() == "Windows":
    # Configurações de conexão
    config = {
        'user': 'root',
        'password': '253690',
        'host': 'localhost',
        'database': 'compras',
        'raise_on_warnings': True,
    }
else:
    # Configurações de conexão
    config = {
        'user': 'root',
        'password': 'Paiva2003',
        'host': 'localhost',
        'database': 'compras',
        'raise_on_warnings': True,
        'auth_plugin': 'mysql_native_password'
    }


# Conectar ao banco de dados
conn = mysql.connector.connect(**config)


# =====================================================Funções==========================================================

# Funções para alternar telas
def mostrar_tela1():
    frame1.pack(fill="both", expand=True)
    frame2.pack_forget()
    frame3.pack_forget()
    frame4.pack_forget()



def mostrar_tela2():
    frame1.pack_forget()
    frame2.pack(fill="both", expand=True)
    frame3.pack_forget()
    frame4.pack_forget()


def mostrar_tela3():
    frame1.pack_forget()
    frame2.pack_forget()
    frame3.pack(fill="both", expand=True)
    frame4.pack_forget()

    try:
        conn = mysql.connector.connect(**config)
        if conn.is_connected():
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM cotacoes WHERE SITUACAO='ABERTO'")
            cotacoes_abertas = cursor.fetchall()

            for widget in frame3.winfo_children():
                widget.destroy()

            titulo3 = ctk.CTkLabel(frame3, text="COMPRAS PENDENTES", font=("Arial", 20))
            titulo3.place(x=570, y=5)

            botao_tela1 = ctk.CTkButton(frame3, text="Voltar", command=mostrar_tela1, width=50)
            botao_tela1.place(x=10, y=10)

            y_position = 100
            botoes_cotacoes.clear()
            checkboxGlobal.clear()
            botao_deletarCotacao.clear()
            for index, row in enumerate(cotacoes_abertas):
                botao_cotacao = ctk.CTkButton(frame3, text=f"Cotação: {row['COTACAO']}",
                                              command=lambda r=row, b=index: perguntar_fornecedores(r, b))
                botao_cotacao.place(x=100, y=y_position)
                botoes_cotacoes.append(botao_cotacao)

                check_var = ctk.StringVar(value=row['CHECKBOX_STATE'])
                checkbox = ctk.CTkCheckBox(frame3, text="ENVIADO PARA APROVAÇÃO",
                                                     variable=check_var, onvalue="on", offvalue="off",
                                                     command=lambda r=row, v=check_var: salvar_estado_checkbox(r, v))
                checkbox.place(x=250, y=y_position)
                checkboxGlobal.append(checkbox)

                botao_delete = ctk.CTkButton(frame3, text="DELETAR", width=70,
                                             command=lambda r=row, b=index: botao_deletar(r, b))
                botao_delete.place(x=470, y=y_position)
                botao_deletarCotacao.append(botao_delete)

                y_position += 50
    except mysql.connector.Error as e:
        print("Erro ao conectar ao MySQL", e)
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

def mostrar_tela4():
    frame1.pack_forget()
    frame2.pack_forget()
    frame3.pack_forget()
    frame4.pack(fill="both", expand=True)




# Funções de eventos
def salvar_estado_checkbox(row, check_var):
    try:
        conn = mysql.connector.connect(**config)
        if conn.is_connected():
            cursor = conn.cursor()
            query = "UPDATE cotacoes SET CHECKBOX_STATE=%s WHERE ID=%s"
            data = (check_var.get(), row['ID'])
            cursor.execute(query, data)
            conn.commit()
    except mysql.connector.Error as e:
        print("Erro ao conectar ao MySQL", e)
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()


def abrir_top_level(row, index, cotacao_id=None):
    top = ctk.CTkToplevel()
    top.geometry("600x400")
    top.attributes('-topmost', True)

    fornecedor_entry = ctk.CTkEntry(top, placeholder_text="FORNECEDOR")
    fornecedor_entry.place(x=50, y=50)

    unico_entry = ctk.CTkEntry(top, placeholder_text="Nº UNICO")
    unico_entry.place(x=50, y=100)

    pedido_entry = ctk.CTkEntry(top, placeholder_text="Nº PEDIDO")
    pedido_entry.place(x=50, y=150)

    observacao_entry = ctk.CTkEntry(top, placeholder_text="OBSERVAÇÃO")
    observacao_entry.place(x=50, y=250)

    titulo4 = ctk.CTkLabel(top, text="Modelo de observação do pedido", font=("Arial", 10))
    titulo4.place(x=250, y=50)

    textbox2 = ctk.CTkTextbox(top, width=300, height=200)
    textbox2.place(x=250, y=100)

    var_empresa = None
    if row['EMPRESA'] == "CREDICAR":
        var_empresa = "22.257.109/0003-03"
    elif row['EMPRESA'] == "LUIZ VIANA":
        var_empresa = "07.590.934/0002-50"
    elif row['EMPRESA'] == "LOC MINAS":
        var_empresa = "18.778.140/0002-31"
    elif row['EMPRESA'] == "LOC RIO":
        var_empresa = "18.778.116/0002-00"
    elif row['EMPRESA'] == "VIANA":
        var_empresa = "19.001.883/0002-63"
    else:
        var_empresa = "45.034.664/0002-90"

    if row['VEICULO'] == None and row['NATUREZA'] != 'PEDIDO FAKE':
        row['VEICULO'] = "REPOSIÇÃO DE ESTOQUE"
    elif row['VEICULO'] == None and row['NATUREZA'] == 'PEDIDO FAKE':
        row['VEICULO'] = "PEDIDO FAKE"

    textbox2.insert(0.0,
                    "RETIRA - FILIAL " + f"{row['BASE']} - \n" + f"{row['VEICULO']} - \n" + f"{row['NATUREZA']}\n" +
                    "COMPRADOR JADILSON\n" + f"FATURAR NO CNPJ: {var_empresa}")

    def salvar_dados():
        try:
            conn = mysql.connector.connect(**config)
            if conn.is_connected():
                cursor = conn.cursor()
                if cotacao_id:
                    query = """
                        UPDATE cotacoes 
                        SET FORNECEDOR=%s, NUMERO_UNICO=%s, NUMERO_PEDIDO=%s, OBSERVACAO=%s, SITUACAO='FECHADO' 
                        WHERE ID=%s
                    """
                    data = (
                        fornecedor_entry.get(), unico_entry.get(), pedido_entry.get(),
                        observacao_entry.get(), cotacao_id
                    )
                else:
                    query = """
                        INSERT INTO cotacoes (COTACAO, DATA, VEICULO, SITUACAO, FORNECEDOR, NUMERO_UNICO, NUMERO_PEDIDO,
                         NATUREZA, EMPRESA, BASE, OBSERVACAO)
                        VALUES (%s, %s, %s, 'FECHADO', %s, %s, %s, %s, %s, %s, %s)
                    """
                    data = (
                        row['COTACAO'], row['DATA'], row['VEICULO'], fornecedor_entry.get(), unico_entry.get(),
                        pedido_entry.get(), row['NATUREZA'], row['EMPRESA'], row['BASE'], observacao_entry.get()
                    )
                cursor.execute(query, data)
                conn.commit()
                top.destroy()
                if (cotacao_id is None and index < len(botoes_cotacoes) and index < len(checkboxGlobal)
                        and index < len(botao_deletarCotacao)):
                    botoes_cotacoes[index].destroy()
                    checkboxGlobal[index].destroy()
                    botao_deletarCotacao[index].destroy()
        except mysql.connector.Error as e:
            print("Erro ao conectar ao MySQL", e)
        finally:
            if conn.is_connected():
                cursor.close()
                conn.close()

    salvar_button = ctk.CTkButton(top, text="Salvar", command=salvar_dados)
    salvar_button.place(x=150, y=350)


def clonar_cotacoes(num_fornecedores, row):
    try:
        conn = mysql.connector.connect(**config)
        if conn.is_connected():
            cursor = conn.cursor()
            cotacao_ids = []
            for i in range(num_fornecedores):
                query = """
                    INSERT INTO cotacoes (COTACAO, DATA, VEICULO, SITUACAO, FORNECEDOR, NUMERO_UNICO, NUMERO_PEDIDO,
                     NATUREZA, EMPRESA, BASE, OBSERVACAO)
                    VALUES (%s, %s, %s, 'ABERTO', %s, %s, %s, %s, %s, %s, %s)
                """

                data = (
                    row['COTACAO'], row['DATA'], row['VEICULO'], None, None, None, row['NATUREZA'], row['EMPRESA'],
                    row['BASE'], None
                )
                cursor.execute(query, data)
                cotacao_ids.append(cursor.lastrowid)
                conn.commit()
            return cotacao_ids
    except mysql.connector.Error as e:
        print("Erro ao conectar ao MySQL", e)
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()


def botao_deletar(row, index):
    try:
        conn = mysql.connector.connect(**config)
        if conn.is_connected():
            cursor = conn.cursor()
            query = "DELETE FROM cotacoes WHERE ID=%s"
            data = (row['ID'],)
            cursor.execute(query, data)
            conn.commit()

            # Remover os widgets da interface gráfica
            botoes_cotacoes[index].destroy()
            checkboxGlobal[index].destroy()
            botao_deletarCotacao[index].destroy()



    except mysql.connector.Error as e:
        print("Erro ao conectar ao MySQL", e)
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()


def perguntar_fornecedores(row, index):
    top2 = ctk.CTkToplevel()
    top2.geometry("300x200")
    top2.attributes('-topmost', True)

    fornecedores_label = ctk.CTkLabel(top2, text="Quantos fornecedores foram fechados?")
    fornecedores_label.place(x=50, y=50)

    fornecedores_entry = ctk.CTkEntry(top2, placeholder_text="Número de fornecedores")
    fornecedores_entry.place(x=50, y=100)

    def confirmar_fornecedores():
        num_fornecedores = int(fornecedores_entry.get())
        top2.destroy()

        # Abre a primeira janela com a cotação original
        abrir_top_level(row, index)

        # Clona as cotações para os fornecedores adicionais
        cotacao_ids = clonar_cotacoes(num_fornecedores - 1, row)
        for i, cotacao_id in enumerate(cotacao_ids):
            abrir_top_level(row, index, cotacao_id=cotacao_id)

        # Deleta a cotação original
        deletar_cotacao_original(row['ID'])

    confirmar_button = ctk.CTkButton(top2, text="Confirmar", command=confirmar_fornecedores)
    confirmar_button.place(x=100, y=150)


def deletar_cotacao_original(cotacao_id):
    try:
        conn = mysql.connector.connect(**config)
        if conn.is_connected():
            cursor = conn.cursor()
            query = "DELETE FROM cotacoes WHERE ID=%s"
            data = (cotacao_id,)
            cursor.execute(query, data)
            conn.commit()
    except mysql.connector.Error as e:
        print("Erro ao conectar ao MySQL", e)
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()


# ====================================================DASHBOARD================================================================

# Função para ir para a DashBoard
def funcao_botao2():
    janela_pecas = ctk.CTkToplevel()
    janela_pecas.attributes('-fullscreen', True)  # Configura a janela para ser tela cheia
    janela_pecas.attributes('-topmost', True)
    janela_pecas.configure(fg_color="#111111")

    # Função para sair do modo full-screen
    def sair_full_screen():
        janela_pecas.attributes('-fullscreen', False)
        janela_pecas.destroy()

    botao_sair = ctk.CTkButton(janela_pecas, text="Sair do Modo Full-Screen", command=sair_full_screen)
    botao_sair.pack(pady=20)  # Adiciona um botão para sair do modo full-screen

    # Consulta ao banco de dados
    dados = pd.read_sql(
        sql="SELECT * FROM cotacoes",
        con= mysql.connector.connect(**config)
    )

    # Criar o gráfico Plotly

    # cria o grafico da natureza por bases
    fig = px.histogram(dados, x="NATUREZA",
                       text_auto=True,
                       title="Compras por natureza",
                       color="BASE",
                       template="plotly_dark",
                       width= 500,
                       height= 400)

    # Cria o grafico de quantidade por fornecedores
    fig2 = px.histogram(dados, x="FORNECEDOR", template="plotly_dark", width=1000, height=350)

    # Cria o grafico EM PIZZA
    dados1 = dados[dados["NATUREZA"] == "ESTOQUE"]
    dados2 = dados[dados["NATUREZA"] == "OFICINA"]
    dados3 = dados[dados["NATUREZA"] == "RESSARCIMENTO"]
    dados4 = dados[dados["NATUREZA"] == "PEDIDO FAKE"]

    # Extraindo os valores numéricos
    vESTOQUE = dados1["NATUREZA"].value_counts().get("ESTOQUE", 0)
    vOFICINA = dados2["NATUREZA"].value_counts().get("OFICINA", 0)
    vRESSARCIMENTO = dados3["NATUREZA"].value_counts().get("RESSARCIMENTO", 0)
    vPEDIDO_FAKE = dados4["NATUREZA"].value_counts().get("PEDIDO FAKE", 0)

    labels = ['ESTOQUE', 'OFICINA', 'RESSARCIMENTO', 'PEDIDO FAKE']
    valores = [vESTOQUE, vOFICINA, vRESSARCIMENTO, vPEDIDO_FAKE]

    fig3 = px.pie(values=valores, names=labels, template="plotly_dark", width= 500, height= 400)

    # Salvar o gráfico como uma imagem PNG temporária
    img_path = "grafico.png"
    fig.write_image(img_path)

    img_path2 = "grafico2.png"
    fig2.write_image(img_path2)

    img_path3 = "grafico3.png"
    fig3.write_image(img_path3)

    # Carregar a imagem usando PIL
    img = Image.open(img_path)
    img = img.resize((500, 400))  # Redimensiona a imagem para caber na janela
    img_tk = ImageTk.PhotoImage(img)

    img2 = Image.open(img_path2)
    img2 = img2.resize((1000, 350))  # Redimensiona a imagem para caber na janela
    img_tk2 = ImageTk.PhotoImage(img2)

    img3 = Image.open(img_path3)
    img3 = img3.resize((500, 400))  # Redimensiona a imagem para caber na janela
    img_tk3 = ImageTk.PhotoImage(img3)

    # Cria um rótulo para exibir a imagem
    lbl_img = ctk.CTkLabel(janela_pecas, image=img_tk, text="")
    lbl_img.image = img_tk  # Necessário para evitar que a imagem seja coletada pelo garbage collector
    lbl_img.place(x=100, y=50)

    lbl_img2 = ctk.CTkLabel(janela_pecas, image=img_tk2, text="")
    lbl_img2.image = img_tk2  # Necessário para evitar que a imagem seja coletada pelo garbage collector
    lbl_img2.place(x=100, y=500)

    # Cria um rótulo para exibir a imagem
    lbl_img3 = ctk.CTkLabel(janela_pecas, image=img_tk3, text="")
    lbl_img3.image = img_tk3  # Necessário para evitar que a imagem seja coletada pelo garbage collector
    lbl_img3.place(x=765, y=50)

    # Remove o arquivo de imagem temporário
    os.remove(img_path)
    os.remove(img_path2)
    os.remove(img_path3)


    #graficos interativos
    texto1_Dashboard = ctk.CTkLabel(janela_pecas, text="Graficos interativos", font=("Arial", 15))
    texto1_Dashboard.place(x= 1150, y= 500)

    def ver_graf1():
        # Consulta ao banco de dados
        dados = pd.read_sql(
            sql="SELECT * FROM cotacoes",
            con= mysql.connector.connect(**config)
        )

        # cria o grafico da natureza por bases
        graf1 = px.histogram(dados, x="NATUREZA",
                           text_auto=True,
                           title="Compras por natureza",
                           color="BASE")

        """
                      Como o linux não suporta o arquivo os.startfile(), criei uma condição que se comportará mediante o sistema
                    operacional. (lenbrando que ainda é necessario a alteração do local do arquivo .html)
                """

        caminho_do_arquivo_graf1_linux = r'/home/jadilson/PycharmProjects/pythonProject/AssistenteDeCompras/graf1.html'
        caminho_do_arquivo_graf1_windows = r'C:\Users\claudionisio.bonetto\PycharmProjects\pythonProject\python arquivos/AssistenteDeCompras/graf1.html'

        if platform.system() == "Windows":
            if os.path.exists(caminho_do_arquivo_graf1_windows):
                os.remove(caminho_do_arquivo_graf1_windows)
                print("O arquivo foi deletado.")
                graf1.write_html("graf1.html")
                sair_full_screen()
                os.startfile(caminho_do_arquivo_graf1_windows)  # ultilizar no windows
            else:
                graf1.write_html("graf1.html")
                sair_full_screen()
                os.startfile(caminho_do_arquivo_graf1_windows)  # ultilizar no windows
        else:
            if os.path.exists(caminho_do_arquivo_graf1_linux):
                os.remove(caminho_do_arquivo_graf1_linux)
                print("O arquivo foi deletado.")
                graf1.write_html("graf1.html")
                sair_full_screen()
                subprocess.run(["xdg-open", caminho_do_arquivo_graf1_linux])  # ultilizar no linux
            else:
                graf1.write_html("graf1.html")
                sair_full_screen()
                subprocess.run(["xdg-open", caminho_do_arquivo_graf1_linux])  # ultilizar no linux


    def ver_graf2():
        # Consulta ao banco de dados
        dados = pd.read_sql(
            sql="SELECT * FROM cotacoes",
            con= mysql.connector.connect(**config)
        )

        # Cria o grafico de quantidade por fornecedores
        graf2 = px.histogram(dados, x="FORNECEDOR")

        """
              Como o linux não suporta o arquivo os.startfile(), criei uma condição que se comportará mediante o sistema
            operacional. (lenbrando que ainda é necessario a alteração do local do arquivo .html)
        """

        caminho_do_arquivo_graf2_linux = r'/home/jadilson/PycharmProjects/pythonProject/AssistenteDeCompras/graf2.html'
        caminho_do_arquivo_graf2_windows = r'C:\Users\claudionisio.bonetto\PycharmProjects\pythonProject\python arquivos/AssistenteDeCompras/graf2.html'

        if platform.system() == "Windows":
            if os.path.exists(caminho_do_arquivo_graf2_windows):
                os.remove(caminho_do_arquivo_graf2_windows)
                print("O arquivo foi deletado.")
                graf2.write_html("graf2.html")
                sair_full_screen()
                os.startfile(caminho_do_arquivo_graf2_windows)  # ultilizar no windows
            else:
                graf2.write_html("graf2.html")
                sair_full_screen()
                os.startfile(caminho_do_arquivo_graf2_windows)  # ultilizar no windows
        else:
            if os.path.exists(caminho_do_arquivo_graf2_linux):
                os.remove(caminho_do_arquivo_graf2_linux)
                print("O arquivo foi deletado.")
                graf2.write_html("graf2.html")
                sair_full_screen()
                subprocess.run(["xdg-open", caminho_do_arquivo_graf2_linux])  # ultilizar no linux
            else:
                graf2.write_html("graf2.html")
                sair_full_screen()
                subprocess.run(["xdg-open", caminho_do_arquivo_graf2_linux])  # ultilizar no linux


    def ver_graf3():
        # Consulta ao banco de dados
        dados = pd.read_sql(
            sql="SELECT * FROM cotacoes",
            con=mysql.connector.connect(**config)
        )

        # Cria o grafico EM PIZZA
        dados1 = dados[dados["NATUREZA"] == "ESTOQUE"]
        dados2 = dados[dados["NATUREZA"] == "OFICINA"]
        dados3 = dados[dados["NATUREZA"] == "RESSARCIMENTO"]
        dados4 = dados[dados["NATUREZA"] == "PEDIDO FAKE"]

        # Extraindo os valores numéricos
        vESTOQUE = dados1["NATUREZA"].value_counts().get("ESTOQUE", 0)
        vOFICINA = dados2["NATUREZA"].value_counts().get("OFICINA", 0)
        vRESSARCIMENTO = dados3["NATUREZA"].value_counts().get("RESSARCIMENTO", 0)
        vPEDIDO_FAKE = dados4["NATUREZA"].value_counts().get("PEDIDO FAKE", 0)

        labels = ['ESTOQUE', 'OFICINA', 'RESSARCIMENTO', 'PEDIDO FAKE']
        valores = [vESTOQUE, vOFICINA, vRESSARCIMENTO, vPEDIDO_FAKE]

        graf3 = px.pie(values=valores, names=labels)

        """
              Como o linux não suporta o arquivo os.startfile(), criei uma condição que se comportará mediante o sistema
            operacional. (lenbrando que ainda é necessario a alteração do local do arquivo .html)
        """

        caminho_do_arquivo_graf3_linux = r'/home/jadilson/PycharmProjects/pythonProject/AssistenteDeCompras/graf3.html'
        caminho_do_arquivo_graf3_windows = r'C:\Users\claudionisio.bonetto\PycharmProjects\pythonProject\python arquivos/AssistenteDeCompras/graf3.html'


        if platform.system() == "Windows":
            if os.path.exists(caminho_do_arquivo_graf3_windows):
                os.remove(caminho_do_arquivo_graf3_windows)
                print("O arquivo foi deletado.")
                graf3.write_html("graf3.html")
                sair_full_screen()
                os.startfile(caminho_do_arquivo_graf3_windows) # ultilizar no windows
            else:
                graf3.write_html("graf3.html")
                sair_full_screen()
                os.startfile(caminho_do_arquivo_graf3_windows) # ultilizar no windows
        else:
            if os.path.exists(caminho_do_arquivo_graf3_linux):
                os.remove(caminho_do_arquivo_graf3_linux)
                print("O arquivo foi deletado.")
                graf3.write_html("graf3.html")
                sair_full_screen()
                subprocess.run(["xdg-open", caminho_do_arquivo_graf3_linux])  # ultilizar no linux
            else:
                graf3.write_html("graf3.html")
                sair_full_screen()
                subprocess.run(["xdg-open", caminho_do_arquivo_graf3_linux])  # ultilizar no linux




    botao_graf1 = ctk.CTkButton(janela_pecas, text="Grafico 1", command=ver_graf1)
    botao_graf1.place(x=1150, y=550)

    botao_graf2 = ctk.CTkButton(janela_pecas, text="Grafico 2", command=ver_graf2)
    botao_graf2.place(x=1150, y=600)

    botao_graf3 = ctk.CTkButton(janela_pecas, text="Grafico 3", command=ver_graf3)
    botao_graf3.place(x=1150, y=650)

#=======================================TELA DE FORNECEDORES============================================================

#criando o Frame4
frame4 = ctk.CTkFrame(janela)

#botão de voltar
botao_tela1 = ctk.CTkButton(frame4, text="Voltar", command=mostrar_tela1, width=50)
botao_tela1.place(x=10, y=10)

#adicionando titulo do frame4
titulo4 = ctk.CTkLabel(frame4, text="TELA DE FORNECEDORES", font=("Arial", 20))
titulo4.place(x=570, y=5)

#subtítulo do frame4
Subtitulo_frame4 = ctk.CTkLabel(frame4, text="Tipos de fornecedores", font=("Arial", 15))
Subtitulo_frame4.place(x=625 , y=50 )

# posicionando as Tabviews
Tabview = ctk.CTkTabview(master= frame4, fg_color="gray20",width= 900, height= 700)
Tabview.place(x=250, y=100)

# Criando as tabsview
Tabview.add("Funilaria")
Tabview.add("Motor")
Tabview.add("Mecânica")
Tabview.add("Motos")
Tabview.add("Conssecionária")
Tabview.set("Funilaria")    #começará nessa Tabview





#>>>>>>>>>>>>Tabview funilaria
Texto_Tabview_funilaria = ctk.CTkLabel(Tabview.tab("Funilaria"),
                                                 text="Esses são os fonecedores de funilaria:",
                                                 font=("Arial", 20))
Texto_Tabview_funilaria.place(x= 50, y= 50)

# Consulta ao banco de dados
dados2 = pd.read_sql(
    sql="SELECT * FROM fornecedores",
    con=mysql.connector.connect(**config)
)

#pegando somente os fornecedores de funilaria do Banco de Dados
dadosx = dados2[dados2["TipoDeVenda"] == "Funilaria"]

# Transformando os dados em string para exibição
dados_str = dadosx[['codigo','nome', 'vendedor']].to_string(index=False, col_space=30)

dados_Tabview_funilaria = ctk.CTkLabel(Tabview.tab("Funilaria"),
                                                 text= dados_str,
                                                 font=("Arial", 20))
dados_Tabview_funilaria.place(x= 50, y= 150)





#>>>>>>>>>>>>Tabview Motor
Texto_Tabview_motor = ctk.CTkLabel(Tabview.tab("Motor"),
                                                 text="Esses são os fonecedores de Motores (Retífica):",
                                                 font=("Arial", 20))
Texto_Tabview_motor.place(x= 50, y= 50)

#pegando somente os fornecedores de funilaria do Banco de Dados
dadosx2 = dados2[dados2["TipoDeVenda"] == "Motor"]

# Transformando os dados em string para exibição
dados_str2 = dadosx2[['codigo','nome', 'vendedor']].to_string(index=False, col_space=30)

Texto_Tabview_motor = ctk.CTkLabel(Tabview.tab("Motor"),
                                                 text= dados_str2,
                                                 font=("Arial", 20))
Texto_Tabview_motor.place(x= 50, y= 150)





#>>>>>>>>>>>>Tabview Mecânica
Texto_Tabview_Mecânica = ctk.CTkLabel(Tabview.tab("Mecânica"),
                                                 text="Esses são os fonecedores de Mecânica:",
                                                 font=("Arial", 20))
Texto_Tabview_Mecânica.place(x= 50, y= 50)

#pegando somente os fornecedores de funilaria do Banco de Dados
dadosx3 = dados2[dados2["TipoDeVenda"] == "Mecânica"]

# Transformando os dados em string para exibição
dados_str3 = dadosx3[['codigo','nome', 'vendedor']].to_string(index=False, col_space=30)

Texto_Tabview_Mecânica = ctk.CTkLabel(Tabview.tab("Mecânica"),
                                                 text= dados_str3,
                                                 font=("Arial", 20))
Texto_Tabview_Mecânica.place(x= 50, y= 150)





#>>>>>>>>>>>>Tabview Motos
Texto_Tabview_Motos = ctk.CTkLabel(Tabview.tab("Motos"),
                                                 text="Esses são os fonecedores de Motos:",
                                                 font=("Arial", 20))
Texto_Tabview_Motos.place(x= 50, y= 50)

#pegando somente os fornecedores de funilaria do Banco de Dados
dadosx4 = dados2[dados2["TipoDeVenda"] == "Motos"]

# Transformando os dados em string para exibição
dados_str4 = dadosx4[['codigo','nome', 'vendedor']].to_string(index=False, col_space=30)

Texto_Tabview_Motos = ctk.CTkLabel(Tabview.tab("Motos"),
                                                 text= dados_str4,
                                                 font=("Arial", 20))
Texto_Tabview_Motos.place(x= 50, y= 150)





#>>>>>>>>>>>>Tabview Conssecionárias
Texto_Tabview_Conssecionaria = ctk.CTkLabel(Tabview.tab("Conssecionária"),
                                                 text="Esses são os fonecedores de funilaria:",
                                                 font=("Arial", 20))
Texto_Tabview_Conssecionaria.place(x= 50, y= 50)

# Consulta ao banco de dados
dados2 = pd.read_sql(
    sql="SELECT * FROM fornecedores",
    con=mysql.connector.connect(**config)
)

#pegando somente os fornecedores de funilaria do Banco de Dados
dadosx5 = dados2[dados2["TipoDeVenda"] == "Conssecionária"]

# Transformando os dados em string para exibição
dados_str5 = dadosx5[['codigo','nome', 'vendedor']].to_string(index=False, col_space=30)

Texto_Tabview_Conssecionaria = ctk.CTkLabel(Tabview.tab("Conssecionária"),
                                                 text= dados_str5,
                                                 font=("Arial", 20))
Texto_Tabview_Conssecionaria.place(x= 50, y= 150)


# ========================================================FRAME 1=======================================================

# Frame da Tela 1
frame1 = ctk.CTkFrame(janela)
titulo = ctk.CTkLabel(frame1, text="Seja bem vindo ao assistente de compras", font=("Arial", 20),
                                fg_color="#212121")
titulo.place(x=500, y=5)
botao_tela2 = ctk.CTkButton(frame1, text="CENTRAL DE COMPRAS", width=200, command=mostrar_tela2).place(x=580,
                                                                                                                 y=300)
botao_tela3 = ctk.CTkButton(frame1, text="CONTROLE DE COMPRAS", width=200, command=mostrar_tela3).place(x=580,
                                                                                                                  y=400)
botao2 = ctk.CTkButton(frame1, text="DASHBOARD", command=funcao_botao2, width=200).place(x=580, y=500)

botao_tela4 = ctk.CTkButton(frame1, text="FORNECEDORES",command=mostrar_tela4, width=200).place(x=580,y=600)




#======================================================Frame da Tela 2==================================================
frame2 = ctk.CTkFrame(janela)

titulo2 = ctk.CTkLabel(frame2, text="CENTRAL DE COMPRAS", font=("Arial", 20))
titulo2.place(x=570, y=5)


def funcao_botao3():
    def funcao_botao5():
        # Obter a data e hora atuais
        data_atual = datetime.now()
        # Formatar a data como string
        data_formatada = data_atual.strftime("%Y-%m-%d")

        try:
            # Conectar ao banco de dados
            conn = mysql.connector.connect(**config)

            if conn.is_connected():
                cursor = conn.cursor()

                # Obter os valores dos campos e definir como None se estiverem vazios
                veiculo_str = veiculo.get() if veiculo.get() else None
                modelo_int = int(modelo.get()) if modelo.get() else None
                chassi_str = chassi.get() if chassi.get() else None

                # Novos dados a serem adicionados
                new_data = {
                    'COTACAO': cotacao_str,
                    'DATA': data_formatada,
                    'VEICULO': veiculo_str,
                    'SITUACAO': 'ABERTO',
                    'FORNECEDOR': None,
                    'NUMERO_UNICO': None,
                    'NUMERO_PEDIDO': None,
                    'NATUREZA': natureza_str,
                    'EMPRESA': empresa_str,
                    'BASE': base_entry_str,
                    'OBSERVACAO': None
                }

                query = """
                                    INSERT INTO cotacoes (COTACAO, DATA, VEICULO, SITUACAO, FORNECEDOR, NUMERO_UNICO, NUMERO_PEDIDO,
                                     NATUREZA, EMPRESA, BASE, OBSERVACAO)
                                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                                """
                data = (
                    new_data['COTACAO'], new_data['DATA'], new_data['VEICULO'], new_data['SITUACAO'],
                    new_data['FORNECEDOR'], new_data['NUMERO_UNICO'], new_data['NUMERO_PEDIDO'], new_data['NATUREZA'],
                    new_data['EMPRESA'], new_data['BASE'], new_data['OBSERVACAO']
                )
                cursor.execute(query, data)
                conn.commit()

                # Mensagem de confirmação
                confirmacao_label = ctk.CTkLabel(frame2, text="Cotação salva com sucesso", font=("Arial", 15),
                                                           text_color="green")
                confirmacao_label.place(x=585, y=80)
        except mysql.connector.Error as e:
            print("Erro ao conectar ao MySQL", e)
        finally:
            if conn.is_connected():
                cursor.close()
                conn.close()

        def funcao_botao6():
            # Limpar todos os campos de entrada
            cotacao.delete(0, tkinter.END)
            veiculo.delete(0, tkinter.END)
            modelo.delete(0, tkinter.END)
            chassi.delete(0, tkinter.END)
            quant.delete(0, tkinter.END)
            base_entry.delete(0, tkinter.END)
            for entry in vet:
                entry.destroy()  # Destroi cada widget CTkEntry
            textbox.destroy()  # destrói a caixa de texto
            confirmacao_label.destroy()
            botao6.destroy()
            botao7.destroy()
            botao5.destroy()
            titulo3.destroy()

        def funcao_botao7():
            def funcao_botao_EnvioAutomatico():
                # Transforma os campos de entrada em strings e inteiros
                codigo_peca_str = str(codigo_peca.get())
                marca_str = str(marca.get())
                print('Funcionando!')

            def funcao_botao4():
                textbox = ctk.CTkTextbox(top3, width=300, height=200)
                textbox.place(x=50, y=250)

                textbox.insert(0.0, "código da peça\n\n" + "1 = funilaria\n" + "2 = vidro\n" + "3 = caminhão\n"
                               + "4 = mecânico\n" + "5 = internas\n" + "6 = amortecedores\n" + "7 = elétrica\n" + "8 = motos\n" +
                               "9 = vans\n" + "10 = teste\n\n\n" + "códigos da marca\n\n" + "1 = fiat\n" + "2 = chevrolet\n" +
                               "3 = renault\n" + "4 = volkswagen\n" + "5 = teste\n")

            top3 = ctk.CTkToplevel()
            top3.geometry("500x500")
            top3.attributes('-topmost', True)

            codigo_peca = ctk.CTkEntry(top3, placeholder_text="CÓDIGO DA PEÇA")
            codigo_peca.place(x=50, y=50)
            marca = ctk.CTkEntry(top3, placeholder_text="CÓDIGO DA MARCA")
            marca.place(x=50, y=100)
            botao_EnvioAutomatico = ctk.CTkButton(top3, text="ENVIAR",
                                                            command=funcao_botao_EnvioAutomatico,
                                                            fg_color='#008000',
                                                            hover_color='#006400').place(x=50, y=150)
            botao_CODIGOS = ctk.CTkButton(top3, text="CÓDIGOS", command=funcao_botao4).place(x=50, y=200)

        # Transforma todos os dados CTkEntry em seus respectivos tipos de dados
        for i in range(0, quantidade):
            vet_number[i] = vet[i].get()
            vet_str[i] = str(vet_number[i])

        # Cria uma textbox e insere os dados
        textbox = ctk.CTkTextbox(frame2, width=300, height=300)
        textbox.place(x=975, y=75)

        textbox.insert(0.0, f"Veiculo: {veiculo_str}\n"
                            f"Modelo: {modelo_int}\n"
                            f"Chassi: {chassi_str}\n\n"
                            f"Itens:\n")

        for i in range(0, quantidade):
            textbox.insert(tkinter.END, f"- {vet_str[i]}\n")

        botao6 = ctk.CTkButton(frame2, text="CERTO", command=funcao_botao6)
        botao6.place(x=975, y=500)
        botao7 = ctk.CTkButton(frame2, text="ENVIO AUTOMATICO", fg_color='#8B0000', command=funcao_botao7,
                                         hover_color='#800000')
        botao7.place(x=1130, y=500)

    # Obtendo a quantidade de itens
    quantidade_text = quant.get()
    quantidade = int(quantidade_text)

    # Inicializa as listas com CTkEntry widgets
    vet: [int] = [0 for x in range(0, quantidade)]
    vet_number: [int] = [0 for x in range(0, quantidade)]  # Inicialize vet_number
    vet_str: [int] = [0 for x in range(0, quantidade)]  # Inicialize vet_int

    # Adiciona os CTkEntry widgets na janela e posiciona cada um individualmente
    for i in range(0, quantidade):
        vet[i] = ctk.CTkEntry(frame2, placeholder_text=f"item{i + 1}")
        vet[i].place(x=615, y=175 + i * 30)

    # Transforma os campos de entrada em strings e inteiros
    veiculo_str = str(veiculo.get()) if veiculo.get() else None
    cotacao_str = str(cotacao.get())
    modelo_int = int(modelo.get()) if modelo.get() else None
    chassi_str = str(chassi.get()) if chassi.get() else None
    base_entry_str = str(base_entry.get())
    natureza_str = str(natureza.get())
    empresa_str = str(empresa.get())

    botao5 = ctk.CTkButton(frame2, text="Pré-visualizar", width=210, command=funcao_botao5)
    botao5.place(x=575, y=125)

    titulo3 = ctk.CTkLabel(frame2, text="Insira os itens que deseja comprar", font=("Arial", 20),
                                     fg_color="#212121")
    titulo3.place(x=530, y=50)


titulo = ctk.CTkLabel(frame2, text="DADOS DE PEÇAS E VEÍCULOS", fg_color="#212121")
titulo.place(x=80, y=60)
cotacao = ctk.CTkEntry(frame2, placeholder_text="COTAÇÃO")
cotacao.place(x=100, y=100)
veiculo = ctk.CTkEntry(frame2, placeholder_text="VEÍCULO")
veiculo.place(x=100, y=140)
modelo = ctk.CTkEntry(frame2, placeholder_text="MODELO")
modelo.place(x=100, y=180)
chassi = ctk.CTkEntry(frame2, placeholder_text="CHASSI")
chassi.place(x=100, y=220)
base_entry = ctk.CTkEntry(frame2, placeholder_text="BASE")
base_entry.place(x=100, y=260)
natureza = ctk.CTkOptionMenu(frame2,
                                       values=["ESTOQUE", "OFICINA", "RESSARCIMENTO", "PEDIDO FAKE"], )
natureza.place(x=100, y=300)
empresa = ctk.CTkOptionMenu(frame2,
                                      values=["CREDICAR", "LUIZ VIANA", "LOC MINAS", "LOC RIO", "VIANA", "GV"], )
empresa.place(x=100, y=340)
quant = ctk.CTkEntry(frame2, placeholder_text="QUANTOS ITENS?")
quant.place(x=100, y=380)

botao3 = ctk.CTkButton(frame2, text="INICIAR COMPRA", command=funcao_botao3).place(x=100, y=420)

botao_tela1 = ctk.CTkButton(frame2, text="Voltar", command=mostrar_tela1, width=50)
botao_tela1.place(x=10, y=10)

# Frame da Tela 3
frame3 = ctk.CTkFrame(janela)

# Inicializa o frame da Tela 3 sem widgets
titulo3 = ctk.CTkLabel(frame3, text="COMPRAS PENDENTES", font=("Arial", 20))
titulo3.place(x=570, y=5)

botao_tela1 = ctk.CTkButton(frame3, text="Voltar", command=mostrar_tela1, width=50)
botao_tela1.place(x=10, y=10)




# ====================================Loops para manter a Janela ativa==================================================
# Mostra a Tela 1 inicialmente
mostrar_tela1()

janela.mainloop()