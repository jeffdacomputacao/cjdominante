import tkinter as tk
from tkinter import messagebox, simpledialog
from itertools import combinations
import math

import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


class AplicacaoConjuntoDominante:
    def __init__(self, root):
        self.root = root
        self.root.title("Conjunto Dominante Mínimo - Distribuição de Roteadores")
        self.root.geometry("1280x780")
        self.root.configure(bg="#f4f4f4")

        self.linhas = 8
        self.colunas = 10

        self.comodos = {}      # nome -> {"linha": x, "coluna": y, "botao": ref}
        self.posicoes = {}     # (linha, coluna) -> nome
        self.grafo = {}        # nome -> lista de vizinhos

        self.modo_visualizacao = "grade"   # "grade" ou "grafo"
        self.canvas_grafo = None
        self.figura_grafo = None

        self.criar_interface()

    # =========================================================
    # INTERFACE
    # =========================================================
    def criar_interface(self):
        self.frame_esquerdo = tk.Frame(self.root, bg="#e9ecef", width=240, padx=10, pady=10)
        self.frame_esquerdo.pack(side="left", fill="y")

        self.frame_centro = tk.Frame(self.root, bg="white", padx=10, pady=10)
        self.frame_centro.pack(side="left", fill="both", expand=True)

        self.frame_direito = tk.Frame(self.root, bg="#f8f9fa", width=320, padx=10, pady=10)
        self.frame_direito.pack(side="right", fill="y")

        self.criar_painel_controle()
        self.criar_area_central()
        self.criar_painel_resultados()

    def criar_painel_controle(self):
        titulo = tk.Label(
            self.frame_esquerdo,
            text="CONTROLES",
            font=("Arial", 14, "bold"),
            bg="#e9ecef"
        )
        titulo.pack(pady=(0, 15))

        tk.Label(self.frame_esquerdo, text="Linhas:", bg="#e9ecef").pack(anchor="w")
        self.entry_linhas = tk.Entry(self.frame_esquerdo)
        self.entry_linhas.insert(0, str(self.linhas))
        self.entry_linhas.pack(fill="x", pady=(0, 10))

        tk.Label(self.frame_esquerdo, text="Colunas:", bg="#e9ecef").pack(anchor="w")
        self.entry_colunas = tk.Entry(self.frame_esquerdo)
        self.entry_colunas.insert(0, str(self.colunas))
        self.entry_colunas.pack(fill="x", pady=(0, 10))

        tk.Button(
            self.frame_esquerdo,
            text="Criar Grade",
            command=self.recriar_grade,
            bg="#0d6efd",
            fg="white",
            font=("Arial", 10, "bold")
        ).pack(fill="x", pady=5)

        tk.Label(self.frame_esquerdo, text="Alcance do sinal:", bg="#e9ecef").pack(anchor="w", pady=(15, 0))
        self.entry_alcance = tk.Entry(self.frame_esquerdo)
        self.entry_alcance.insert(0, "2.5")
        self.entry_alcance.pack(fill="x", pady=(0, 10))

        tk.Button(
            self.frame_esquerdo,
            text="Gerar Grafo",
            command=self.gerar_grafo_automaticamente,
            bg="#198754",
            fg="white",
            font=("Arial", 10, "bold")
        ).pack(fill="x", pady=5)

        tk.Button(
            self.frame_esquerdo,
            text="Executar Baseline",
            command=self.executar_baseline,
            bg="#dc3545",
            fg="white",
            font=("Arial", 10, "bold")
        ).pack(fill="x", pady=5)

        tk.Button(
            self.frame_esquerdo,
            text="Voltar para Grade",
            command=self.mostrar_grade,
            bg="#6610f2",
            fg="white",
            font=("Arial", 10, "bold")
        ).pack(fill="x", pady=5)

        tk.Button(
            self.frame_esquerdo,
            text="Limpar Tudo",
            command=self.limpar_tudo,
            bg="#6c757d",
            fg="white",
            font=("Arial", 10, "bold")
        ).pack(fill="x", pady=5)

        explicacao = (
            "Como usar:\n"
            "1. Defina linhas e colunas\n"
            "2. Clique na grade para criar cômodos\n"
            "3. Informe o alcance\n"
            "4. Gere o grafo\n"
            "5. Execute o baseline\n"
            "6. Veja o conjunto dominante no grafo"
        )
        tk.Label(
            self.frame_esquerdo,
            text=explicacao,
            justify="left",
            bg="#e9ecef",
            wraplength=200
        ).pack(pady=(20, 0), anchor="w")

    def criar_area_central(self):
        self.label_centro = tk.Label(
            self.frame_centro,
            text="PLANTA DO AMBIENTE",
            font=("Arial", 14, "bold"),
            bg="white"
        )
        self.label_centro.pack(pady=(0, 10))

        self.container_visual = tk.Frame(self.frame_centro, bg="white")
        self.container_visual.pack(fill="both", expand=True)

        self.frame_grade = tk.Frame(self.container_visual, bg="white")
        self.frame_grade.pack(expand=True)

        self.frame_grafo = tk.Frame(self.container_visual, bg="white")

        self.botoes_grade = []
        self.desenhar_grade()

    def criar_painel_resultados(self):
        titulo = tk.Label(
            self.frame_direito,
            text="RESULTADOS",
            font=("Arial", 14, "bold"),
            bg="#f8f9fa"
        )
        titulo.pack(pady=(0, 15))

        self.texto_resultados = tk.Text(
            self.frame_direito,
            width=38,
            height=38,
            font=("Consolas", 10),
            wrap="word"
        )
        self.texto_resultados.pack(fill="both", expand=True)

        self.atualizar_resultados_iniciais()

    # =========================================================
    # GRADE
    # =========================================================
    def desenhar_grade(self):
        for widget in self.frame_grade.winfo_children():
            widget.destroy()

        self.botoes_grade = []

        for i in range(self.linhas):
            linha_botoes = []
            for j in range(self.colunas):
                botao = tk.Button(
                    self.frame_grade,
                    text="",
                    width=7,
                    height=3,
                    bg="white",
                    command=lambda x=i, y=j: self.clique_celula(x, y)
                )
                botao.grid(row=i, column=j, padx=2, pady=2)
                linha_botoes.append(botao)
            self.botoes_grade.append(linha_botoes)

    def recriar_grade(self):
        try:
            novas_linhas = int(self.entry_linhas.get())
            novas_colunas = int(self.entry_colunas.get())

            if novas_linhas <= 0 or novas_colunas <= 0:
                raise ValueError

            self.linhas = novas_linhas
            self.colunas = novas_colunas

            self.comodos.clear()
            self.posicoes.clear()
            self.grafo.clear()

            self.desenhar_grade()
            self.mostrar_grade()
            self.atualizar_resultados_iniciais()

        except ValueError:
            messagebox.showerror("Erro", "Linhas e colunas devem ser números inteiros positivos.")

    def clique_celula(self, linha, coluna):
        if self.modo_visualizacao != "grade":
            return

        posicao = (linha, coluna)

        if posicao in self.posicoes:
            nome_atual = self.posicoes[posicao]
            resposta = messagebox.askyesno(
                "Remover cômodo",
                f"O cômodo '{nome_atual}' já está nesta célula.\nDeseja remover?"
            )
            if resposta:
                self.remover_comodo(nome_atual)
            return

        nome = simpledialog.askstring(
            "Cadastrar cômodo",
            f"Informe o nome do cômodo para a posição ({linha}, {coluna}):"
        )

        if nome is None:
            return

        nome = nome.strip()

        if not nome:
            messagebox.showwarning("Aviso", "O nome do cômodo não pode ser vazio.")
            return

        if nome in self.comodos:
            messagebox.showwarning("Aviso", "Já existe um cômodo com esse nome.")
            return

        self.adicionar_comodo(nome, linha, coluna)

    def adicionar_comodo(self, nome, linha, coluna):
        botao = self.botoes_grade[linha][coluna]
        botao.config(text=nome, bg="#87ceeb")

        self.comodos[nome] = {
            "linha": linha,
            "coluna": coluna,
            "botao": botao
        }
        self.posicoes[(linha, coluna)] = nome

        self.atualizar_painel_comodos()

    def remover_comodo(self, nome):
        linha = self.comodos[nome]["linha"]
        coluna = self.comodos[nome]["coluna"]
        botao = self.comodos[nome]["botao"]

        botao.config(text="", bg="white", fg="black")

        del self.posicoes[(linha, coluna)]
        del self.comodos[nome]

        if nome in self.grafo:
            del self.grafo[nome]

        for vertice in self.grafo:
            if nome in self.grafo[vertice]:
                self.grafo[vertice].remove(nome)

        self.atualizar_painel_comodos()

    # =========================================================
    # TROCA DE VISUALIZAÇÃO
    # =========================================================
    def mostrar_grade(self):
        self.frame_grafo.pack_forget()
        self.frame_grade.pack(expand=True)
        self.label_centro.config(text="PLANTA DO AMBIENTE")
        self.modo_visualizacao = "grade"

    def mostrar_area_grafo(self):
        self.frame_grade.pack_forget()
        self.frame_grafo.pack(fill="both", expand=True)
        self.label_centro.config(text="GRAFO GERADO")
        self.modo_visualizacao = "grafo"

    # =========================================================
    # GERAÇÃO DO GRAFO
    # =========================================================
    def calcular_distancia(self, comodo1, comodo2):
        x1 = self.comodos[comodo1]["linha"]
        y1 = self.comodos[comodo1]["coluna"]
        x2 = self.comodos[comodo2]["linha"]
        y2 = self.comodos[comodo2]["coluna"]

        return math.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)

    def gerar_grafo_automaticamente(self):
        if len(self.comodos) == 0:
            messagebox.showwarning("Aviso", "Cadastre pelo menos um cômodo na grade.")
            return

        try:
            alcance = float(self.entry_alcance.get())
            if alcance <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Erro", "O alcance deve ser um número positivo.")
            return

        self.grafo = {nome: [] for nome in self.comodos.keys()}
        nomes = list(self.comodos.keys())

        for i in range(len(nomes)):
            for j in range(i + 1, len(nomes)):
                c1 = nomes[i]
                c2 = nomes[j]
                distancia = self.calcular_distancia(c1, c2)

                if distancia <= alcance:
                    self.grafo[c1].append(c2)
                    self.grafo[c2].append(c1)

        self.atualizar_painel_grafo()
        self.desenhar_grafo()
        self.mostrar_area_grafo()

        messagebox.showinfo("Sucesso", "Grafo gerado automaticamente com base na distância.")

    # =========================================================
    # DESENHO DO GRAFO
    # =========================================================
    def desenhar_grafo(self, conjunto_dominante=None):
        for widget in self.frame_grafo.winfo_children():
            widget.destroy()

        G = nx.Graph()

        for nome in self.grafo:
            G.add_node(nome)

        for nome, vizinhos in self.grafo.items():
            for vizinho in vizinhos:
                G.add_edge(nome, vizinho)

        if len(G.nodes) == 0:
            return

        figura = plt.Figure(figsize=(7, 6), dpi=100)
        ax = figura.add_subplot(111)

        posicoes = {}
        for nome in self.comodos:
            # inverte linha no eixo y só para a visualização ficar mais natural
            x = self.comodos[nome]["coluna"]
            y = -self.comodos[nome]["linha"]
            posicoes[nome] = (x, y)

        cores = []
        for no in G.nodes():
            if conjunto_dominante and no in conjunto_dominante:
                cores.append("crimson")
            else:
                cores.append("skyblue")

        nx.draw(
            G,
            posicoes,
            ax=ax,
            with_labels=True,
            node_color=cores,
            node_size=2200,
            font_size=9,
            font_weight="bold",
            edge_color="gray",
            width=2
        )

        titulo = "Grafo do Ambiente"
        if conjunto_dominante:
            titulo = "Grafo com Conjunto Dominante Mínimo"
        ax.set_title(titulo)
        ax.axis("off")

        self.figura_grafo = figura
        self.canvas_grafo = FigureCanvasTkAgg(figura, master=self.frame_grafo)
        self.canvas_grafo.draw()
        self.canvas_grafo.get_tk_widget().pack(fill="both", expand=True)

    # =========================================================
    # BASELINE - FORÇA BRUTA
    # =========================================================
    def domina_tudo(self, conjunto):
        cobertos = set()

        for sala in conjunto:
            cobertos.add(sala)
            cobertos.update(self.grafo[sala])

        return cobertos == set(self.grafo.keys())

    def achar_conjunto_dominante_minimo(self):
        vertices = list(self.grafo.keys())

        for tamanho in range(1, len(vertices) + 1):
            for grupo in combinations(vertices, tamanho):
                if self.domina_tudo(grupo):
                    return set(grupo)

        return set(vertices)

    def executar_baseline(self):
        if len(self.comodos) == 0:
            messagebox.showwarning("Aviso", "Cadastre os cômodos antes de executar.")
            return

        if len(self.grafo) == 0:
            messagebox.showwarning("Aviso", "Gere o grafo antes de executar o baseline.")
            return

        conjunto_dominante = self.achar_conjunto_dominante_minimo()

        self.desenhar_grafo(conjunto_dominante)
        self.mostrar_area_grafo()
        self.mostrar_resultado_final(conjunto_dominante)

    # =========================================================
    # RESULTADOS
    # =========================================================
    def limpar_tudo(self):
        self.comodos.clear()
        self.posicoes.clear()
        self.grafo.clear()
        self.desenhar_grade()
        self.mostrar_grade()
        self.atualizar_resultados_iniciais()

    def atualizar_resultados_iniciais(self):
        self.texto_resultados.delete("1.0", tk.END)
        self.texto_resultados.insert(tk.END, "Sistema pronto.\n")
        self.texto_resultados.insert(tk.END, "\nCadastre os cômodos na grade.\n")

    def atualizar_painel_comodos(self):
        self.texto_resultados.delete("1.0", tk.END)
        self.texto_resultados.insert(tk.END, "CÔMODOS CADASTRADOS\n")
        self.texto_resultados.insert(tk.END, "-" * 35 + "\n")

        if not self.comodos:
            self.texto_resultados.insert(tk.END, "Nenhum cômodo cadastrado.\n")
            return

        for nome in sorted(self.comodos.keys()):
            linha = self.comodos[nome]["linha"]
            coluna = self.comodos[nome]["coluna"]
            self.texto_resultados.insert(
                tk.END,
                f"{nome} -> posição ({linha}, {coluna})\n"
            )

    def atualizar_painel_grafo(self):
        self.texto_resultados.delete("1.0", tk.END)
        self.texto_resultados.insert(tk.END, "GRAFO GERADO\n")
        self.texto_resultados.insert(tk.END, "-" * 35 + "\n")

        for nome in sorted(self.grafo.keys()):
            vizinhos = self.grafo[nome]
            texto_vizinhos = ", ".join(sorted(vizinhos)) if vizinhos else "nenhum"
            self.texto_resultados.insert(tk.END, f"{nome}: {texto_vizinhos}\n")

    def mostrar_resultado_final(self, conjunto_dominante):
        self.texto_resultados.delete("1.0", tk.END)
        self.texto_resultados.insert(tk.END, "RESULTADO FINAL\n")
        self.texto_resultados.insert(tk.END, "-" * 35 + "\n")

        self.texto_resultados.insert(
            tk.END,
            f"Conjunto dominante mínimo:\n{sorted(conjunto_dominante)}\n\n"
        )

        self.texto_resultados.insert(
            tk.END,
            f"Quantidade de roteadores: {len(conjunto_dominante)}\n"
        )

        percentual = (len(conjunto_dominante) / len(self.comodos)) * 100
        self.texto_resultados.insert(
            tk.END,
            f"Percentual de cômodos com roteador: {percentual:.1f}%\n\n"
        )

        self.texto_resultados.insert(tk.END, "Detalhamento dos cômodos:\n")
        for nome in sorted(self.comodos.keys()):
            if nome in conjunto_dominante:
                self.texto_resultados.insert(tk.END, f"- {nome}: COM ROTEADOR\n")
            else:
                self.texto_resultados.insert(tk.END, f"- {nome}: coberto por vizinhança\n")


if __name__ == "__main__":
    root = tk.Tk()
    app = AplicacaoConjuntoDominante(root)
    root.mainloop()