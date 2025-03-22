import tkinter as tk
from tkinter import ttk, messagebox
from tkinter.filedialog import askopenfilename
import csv
import math
import customtkinter as ctk

def parse_int(texto):
    """
    Converte 'texto' para inteiro.
    Remove 'R$' se presente; se falhar, retorna 0.
    """
    if texto is None:
        return 0
    texto = texto.replace("R$", "").strip()
    try:
        return int(texto)
    except ValueError:
        return 0

class Ticket:
    def __init__(self, nome, valor_str, status="Não alocado"):
        self.nome = nome
        self.valor_str = valor_str  # Ex: "10" ou "R$10"
        self.valor_int = parse_int(valor_str)
        self.status = status
        self.atendente = None
        self.widget = None  # Widget (Frame) que representa o ticket
        self.collapsed = True  # Inicia colapsado

class Atendente:
    def __init__(self, nome, senioridade_str, custo):
        self.nome = nome
        self.senioridade_str = senioridade_str  # Capacidade como string
        self.senioridade_val = parse_int(senioridade_str)
        self.custo = custo
        self.custo_val = parse_int(custo)
        self.tickets_alocados = []
        self.widget = None  # Widget (Frame) que representa o atendente
        self.collapsed = True  # Inicia colapsado

    def soma_tickets(self):
        """Retorna a soma dos valores dos tickets alocados."""
        return sum(tkt.valor_int for tkt in self.tickets_alocados)

    def total_cost(self):
        """
        Calcula o custo total do atendente:
          - Se não houver tickets, retorna 0.
          - Se a soma dos tickets for maior que a capacidade, então:
                total_horas = math.ceil(soma dos tickets / capacidade)
                custo_total = total_horas * custo do atendente
          - Caso contrário, custo_total = custo do atendente.
        """
        if not self.tickets_alocados:
            return 0
        soma = self.soma_tickets()
        if soma > self.senioridade_val:
            total_horas = math.ceil(soma / self.senioridade_val)
            return total_horas * self.custo_val
        else:
            return self.custo_val

class TicketManagerApp:
    def __init__(self, root, tickets_csv=None, persons_csv=None, allocations_csv=None,
                 tickets_data=None, persons_data=None, alloc_data=None):
        self.root = root
        self.root.title("Gerenciador de Tickets e Atendentes")
        self.root.geometry("1100x600")

        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("dark-blue")

        # Variável para armazenar dados do drag & drop
        self.drag_data = {}

        # Listas de dados
        self.tickets = []
        self.atendentes = []

        # Carrega dados estruturados, se fornecidos; caso contrário, tenta CSV
        if tickets_data:
            self.load_tickets_data(tickets_data)
        elif tickets_csv:
            self.load_tickets(tickets_csv)

        if persons_data:
            self.load_persons_data(persons_data)
        elif persons_csv:
            self.load_persons(persons_csv)

        if alloc_data:
            self.load_allocations_data(alloc_data)
        elif allocations_csv:
            self.load_allocations(allocations_csv)

        # Menu superior com botões (menu compacto)
        top_frame = ctk.CTkFrame(self.root)
        top_frame.pack(side=ctk.TOP, fill=ctk.X, padx=2, pady=2)

        btn_add_ticket = ctk.CTkButton(top_frame, text="+ TICKET",
                                   command=self.janela_criar_ticket)
        btn_add_ticket.pack(side=ctk.LEFT, padx=2)

        btn_add_atendente = ctk.CTkButton(top_frame, text="+ ATENDENTE", 
                                      command=self.janela_criar_atendente)
        btn_add_atendente.pack(side=ctk.LEFT, padx=2)
        btn_import_tickets = ctk.CTkButton(top_frame, text="Importar Tickets",
                                       command=self.importar_tickets)
        btn_import_tickets.pack(side=ctk.LEFT, padx=2)
        btn_import_atendentes = ctk.CTkButton(top_frame, text="Importar Atendentes", 
                                          command=self.importar_atendentes)
        btn_import_atendentes.pack(side=ctk.LEFT, padx=2)
        btn_import_alloc = ctk.CTkButton(top_frame, text="Importar Alocações", 
                                     command=self.importar_alocacoes)
        btn_import_alloc.pack(side=ctk.LEFT, padx=2)
        btn_limpar_alocacoes = ctk.CTkButton(top_frame, text="LIMPAR ALOCAÇÕES", 
                                        command=self.limpar_alocacoes, fg_color="#bf243c", hover=False)
        btn_limpar_alocacoes.pack(side=ctk.LEFT, padx=2)
        btn_limpar_tickets = ctk.CTkButton(top_frame, text="LIMPAR TICKETS", 
                                       command=self.limpar_tickets, fg_color="#bf243c", hover=False)
        btn_limpar_tickets.pack(side=ctk.LEFT, padx=2)
        btn_limpar_atendentes = ctk.CTkButton(top_frame, text="LIMPAR ATENDENTES", 
                                          command=self.limpar_atendentes, fg_color="#bf243c", hover=False)
        btn_limpar_atendentes.pack(side=ctk.LEFT, padx=2)
        self.label_instrucoes = ctk.CTkLabel(top_frame, text="Arraste o ticket para o atendente para alocar", fg_color="transparent")
        self.label_instrucoes.pack(side=ctk.LEFT, padx=10)

        # Container principal: Canvas (com scrollbar) e Tabela Resumo
        container = ctk.CTkFrame(self.root)
        container.pack(fill=ctk.BOTH, expand=True)

        frame_canvas = ctk.CTkFrame(container, width=500, height=300)
        frame_canvas.pack(fill=ctk.BOTH, expand=True)

        frame_canvas.grid(row=0, column=0, padx=100, pady=10, sticky="nsew")
        self.canvas = tk.Canvas(frame_canvas, bg="white")
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        v_scroll = tk.Scrollbar(frame_canvas, orient="vertical", command=self.canvas.yview)
        v_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.canvas.configure(yscrollcommand=v_scroll.set)
        frame_canvas.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frame_summary = ctk.CTkFrame(container, fg_color="#fff", border_width=2)
        self.frame_summary.grid(row=0, column=1, sticky="ns")

        # Cria os frames para Tickets e Atendentes dentro do Canvas
        self.frame_tickets = ctk.CTkFrame(self.canvas, fg_color="#f0f0f0", width=300, height=400, border_width=2, border_color="#333")
        self.frame_atendentes = ctk.CTkFrame(self.canvas, fg_color="#f0f0f0", width=300, height=400, border_width=2, border_color="#333")
        self.canvas_tickets_window = self.canvas.create_window(20, 20, anchor="nw", window=self.frame_tickets)
        self.canvas_atend_window = self.canvas.create_window(400, 20, anchor="nw", window=self.frame_atendentes)

        self.atualizar_listas()

    # Métodos para carregar dados a partir de listas estruturadas
    def load_tickets_data(self, data):
        """Carrega tickets a partir de uma lista de dicionários."""
        for row in data:
            nome = row.get("ticket_nome", "").strip()
            valor = row.get("ticket_value", "").strip()
            if any(t.nome.lower() == nome.lower() for t in self.tickets):
                continue
            if nome and valor:
                self.tickets.append(Ticket(nome, valor))

    def load_persons_data(self, data):
        """Carrega atendentes a partir de uma lista de dicionários."""
        for row in data:
            nome = row.get("person_name", "").strip()
            capacidade = row.get("person_capacity", "").strip()
            custo = row.get("person_cost", "").strip()
            if any(a.nome.lower() == nome.lower() for a in self.atendentes):
                continue
            if nome and capacidade and custo:
                self.atendentes.append(Atendente(nome, capacidade, custo))

    def load_allocations_data(self, data):
        """
        Carrega alocações a partir de uma lista de dicionários com chaves:
        "ticket_nome" e "person_name".
        """
        for row in data:
            ticket_nome = row.get("ticket_nome", "").strip()
            person_name = row.get("person_name", "").strip()
            ticket = next((t for t in self.tickets if t.nome.lower() == ticket_nome.lower()), None)
            atendente = next((a for a in self.atendentes if a.nome.lower() == person_name.lower()), None)
            if ticket and atendente:
                if len(atendente.tickets_alocados) < atendente.senioridade_val:
                    if ticket.atendente:
                        ticket.atendente.tickets_alocados.remove(ticket)
                    ticket.status = "Alocado"
                    ticket.atendente = atendente
                    atendente.tickets_alocados.append(ticket)

    # Métodos de carregamento via CSV (mantidos)
    def load_tickets(self, filepath):
        try:
            with open(filepath, newline="", encoding="utf-8") as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    nome = row.get("ticket_nome", "").strip()
                    valor = row.get("ticket_value", "").strip()
                    if any(t.nome.lower() == nome.lower() for t in self.tickets):
                        continue
                    if nome and valor:
                        self.tickets.append(Ticket(nome, valor))
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao carregar tickets:\n{e}")

    def load_persons(self, filepath):
        try:
            with open(filepath, newline="", encoding="utf-8") as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    nome = row.get("person_name", "").strip()
                    capacidade = row.get("person_capacity", "").strip()
                    custo = row.get("person_cost", "").strip()
                    if any(a.nome.lower() == nome.lower() for a in self.atendentes):
                        continue
                    if nome and capacidade and custo:
                        self.atendentes.append(Atendente(nome, capacidade, custo))
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao carregar atendentes:\n{e}")

    def load_allocations(self, filepath):
        try:
            with open(filepath, newline="", encoding="utf-8") as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    ticket_nome = row.get("ticket_nome", "").strip()
                    person_name = row.get("person_name", "").strip()
                    ticket = next((t for t in self.tickets if t.nome.lower() == ticket_nome.lower()), None)
                    atendente = next((a for a in self.atendentes if a.nome.lower() == person_name.lower()), None)
                    if ticket and atendente:
                        if len(atendente.tickets_alocados) < atendente.senioridade_val:
                            if ticket.atendente:
                                ticket.atendente.tickets_alocados.remove(ticket)
                            ticket.status = "Alocado"
                            ticket.atendente = atendente
                            atendente.tickets_alocados.append(ticket)
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao carregar alocações:\n{e}")

    # Alterna o estado colapsado/expandido
    def toggle_ticket(self, ticket):
        ticket.collapsed = not ticket.collapsed
        self.atualizar_listas()

    def toggle_atendente(self, atendente):
        atendente.collapsed = not atendente.collapsed
        self.atualizar_listas()

    def atualizar_listas(self):
        for widget in self.frame_tickets.winfo_children():
            widget.destroy()
        for widget in self.frame_atendentes.winfo_children():
            widget.destroy()

        # Lista de Tickets
        ctk.CTkLabel(self.frame_tickets, text="TICKETS (Arraste para alocar)", font=("Helvetica", 14, "bold"),
                text_color="black").pack(pady=10, padx=30)
        for i, ticket in enumerate(self.tickets):
            bg_color = "#79db79" if ticket.status == "Alocado" else "#d1c21b"
            frame_ticket = ctk.CTkFrame(self.frame_tickets, border_width=2, fg_color=bg_color, border_color="#000")
            frame_ticket.pack(fill=ctk.X, padx=20, pady=5)
            ticket.widget = frame_ticket

            if ticket.collapsed:
                ctk.CTkLabel(frame_ticket, text=f"Ticket: {ticket.nome} - R$ {ticket.valor_str}",
                         font=("Helvetica", 10, "bold"), fg_color=bg_color, text_color="black").pack(padx=15, pady=10)
                btn_expand = ctk.CTkButton(frame_ticket, text="Expand", font=("Helvetica", 10),
                                       command=lambda t=ticket: self.toggle_ticket(t), fg_color="#2e2e2e")
                btn_expand.pack(padx=2, pady=5)
            else:
                ctk.CTkLabel(frame_ticket, text=f"Ticket #{i+1}", font=("Helvetica", 12, "bold"),
                         fg_color=bg_color, text_color="black").pack(pady=2)
                ctk.CTkLabel(frame_ticket, text=f"Nome: {ticket.nome}", fg_color=bg_color, text_color="black").pack(pady=2)
                ctk.CTkLabel(frame_ticket, text=f"Valor: R$ {ticket.valor_str}", fg_color=bg_color, text_color="black").pack(pady=2)
                btn_collapse = ctk.CTkButton(frame_ticket, text="Collapse", font=("Helvetica", 10),
                                         command=lambda t=ticket: self.toggle_ticket(t), fg_color="#2e2e2e")
                btn_collapse.pack(padx=2, pady=5)
            frame_ticket.bind("<ButtonPress-1>", lambda event, t=ticket: self.on_ticket_press(event, t))
            frame_ticket.bind("<B1-Motion>", self.on_ticket_motion)
            frame_ticket.bind("<ButtonRelease-1>", self.on_ticket_release)

        # Lista de Atendentes
        ctk.CTkLabel(self.frame_atendentes, text="ATENDENTES", font=("Helvetica", 14, "bold"), 
                     text_color="black", width=200).pack(pady=10, padx=10)
        for i, atendente in enumerate(self.atendentes):
            frame_atendente = ctk.CTkFrame(self.frame_atendentes, border_width=2, fg_color="#dddddd", border_color="#000")
            frame_atendente.pack(fill=ctk.X, padx=10, pady=10)
            atendente.widget = frame_atendente

            if atendente.collapsed:
                ctk.CTkLabel(frame_atendente, text=f"Atendente: {atendente.nome}",
                         font=("Helvetica", 10, "bold"), fg_color="#dddddd", text_color="black").pack(padx=15, pady=10)
                btn_expand = ctk.CTkButton(frame_atendente, text="Expand", font=("Helvetica", 10),
                                       command=lambda a=atendente: self.toggle_atendente(a), fg_color="#2e2e2e")
                btn_expand.pack(padx=2, pady=5)
            else:
                ctk.CTkLabel(frame_atendente, text=f"Atendente: {atendente.nome}",
                         font=("Helvetica", 10, "bold"), fg_color="#dddddd", text_color="black").pack(anchor="w")
                ctk.CTkLabel(frame_atendente, text=f"Senioridade: {atendente.senioridade_str}",
                         fg_color="#dddddd", text_color="black")
                ctk.CTkLabel(frame_atendente, text=f"Custo: {atendente.custo}",
                         fg_color="#dddddd", text_color="black")
                ctk.CTkLabel(frame_atendente, text=f"Soma dos Tickets: {atendente.soma_tickets()}",
                         fg_color="#dddddd", text_color="black").pack(pady=2)
                ctk.CTkLabel(frame_atendente, text=f"Custo Total: R$ {atendente.total_cost():.2f}",
                         fg_color="#dddddd", text_color="black").pack( pady=2)
                for tkt in atendente.tickets_alocados:
                    ctk.CTkLabel(frame_atendente, text=f"-> {tkt.nome} ({tkt.valor_str})",
                            fg_color="#dddddd", text_color="black", font=("Helvetica", 12, "bold")).pack(anchor="w")
                btn_collapse = ctk.CTkButton(frame_atendente, text="Collapse", font=("Helvetica", 10),
                                         command=lambda a=atendente: self.toggle_atendente(a), fg_color="#2e2e2e")
                btn_collapse.pack(padx=2, pady=5)

        # Desenha as Linhas de Conexão
        self.canvas.delete("link_line")
        self.root.update_idletasks()
        for atendente in self.atendentes:
            soma_val = atendente.soma_tickets()
            if soma_val > atendente.senioridade_val:
                line_color = "red"
            elif soma_val == atendente.senioridade_val:
                line_color = "#006400"
            else:
                line_color = "blue"
            for tkt in atendente.tickets_alocados:
                if atendente.widget and tkt.widget:
                    ax0, ay0 = self.canvas.coords(self.canvas_atend_window)
                    ax_rel = atendente.widget.winfo_x() + atendente.widget.winfo_width() // 2
                    ay_rel = atendente.widget.winfo_y() + atendente.widget.winfo_height() // 2
                    canvas_ax = ax0 + ax_rel
                    canvas_ay = ay0 + ay_rel

                    tx0, ty0 = self.canvas.coords(self.canvas_tickets_window)
                    tx_rel = tkt.widget.winfo_x() + tkt.widget.winfo_width() // 2
                    ty_rel = tkt.widget.winfo_y() + tkt.widget.winfo_height() // 2
                    canvas_tx = tx0 + tx_rel
                    canvas_ty = ty0 + ty_rel

                    self.canvas.create_line(canvas_tx, canvas_ty, canvas_ax, canvas_ay,
                                              arrow=tk.LAST, fill=line_color, width=2, tags="link_line")

        self.update_summary()
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
    def update_summary(self):
        # Limpa o conteúdo anterior do frame de resumo
        for widget in self.frame_summary.winfo_children():
            widget.destroy()

        # Calcula os valores para exibir
        total_tickets = len(self.tickets)
        tickets_alocados = sum(1 for t in self.tickets if t.status == "Alocado")
        total_atendentes = len(self.atendentes)
        total_senioridade = sum(a.senioridade_val for a in self.atendentes)
        total_valor_tickets = sum(t.valor_int for t in self.tickets if t.status == "Alocado")
        custo_total = sum(a.total_cost() for a in self.atendentes)

        # Cria um "card" (Frame) com borda e fundo claro
        card_frame = ctk.CTkFrame(self.frame_summary, border_width=2, fg_color="#f9f9f9", width=300)
        card_frame.pack(padx=10, pady=10, fill="both", expand=True)

        # Título em destaque
        ctk.CTkLabel(card_frame,
                text="RESUMO",
                font=("Helvetica", 16, "bold"),
                fg_color="#f9f9f9",
                text_color="#333",
                width=300).pack(pady=(10,5))

        # Subtítulo ou descrição
        ctk.CTkLabel(card_frame,
                text="Visão geral dos dados atuais",
                font=("Helvetica", 10),
                fg_color="#333",
                text_color="#f9f9f9").pack(pady=(0,10))

        # Cria uma fonte para os destaques
        highlight_font = ("Helvetica", 11, "bold")

        # Exibe informações gerais (podem ficar com fonte normal)
        ctk.CTkLabel(card_frame,
                text=f"Total de Tickets: {total_tickets}",
                font=("Helvetica", 12),
                fg_color="#f9f9f9",
                text_color="#333").pack(padx=10, pady=1)

        ctk.CTkLabel(card_frame,
                text=f"Tickets Alocados: {tickets_alocados}",
                font=("Helvetica", 12),
                fg_color="#f9f9f9",
                text_color="#333").pack(padx=10, pady=1)

        ctk.CTkLabel(card_frame,
                text=f"Total de Atendentes: {total_atendentes}",
                font=("Helvetica", 12),
                fg_color="#f9f9f9",
                text_color="#333").pack(padx=10, pady=1)

        # Separador visual
        separator = ctk.CTkFrame(card_frame, height=2, border_width=0, fg_color="#ddd")
        separator.pack(fill="x", padx=10, pady=10)

        # Exibe os valores em destaque
        ctk.CTkLabel(card_frame,
                text=f"Senioridade Total: {total_senioridade}",
                font=highlight_font,
                fg_color="#f9f9f9",
                text_color="#444").pack(anchor="w", padx=10, pady=5)

        ctk.CTkLabel(card_frame,
                text=f"Total de Valor (Tickets): R$ {total_valor_tickets}",
                font=highlight_font,
                fg_color="#f9f9f9",
                text_color="#444").pack(anchor="w", padx=10, pady=5)

        ctk.CTkLabel(card_frame,
                text=f"Custo Total: R$ {custo_total:.2f}",
                font=("Helvetica", 12, "bold"),
                fg_color="#f9f9f9",
                text_color="#aa0000").pack(anchor="w", padx=10, pady=5)

    # def update_summary(self):
    #     for widget in self.frame_summary.winfo_children():
    #         widget.destroy()
    #     total_tickets = len(self.tickets)
    #     tickets_alocados = sum(1 for t in self.tickets if t.status == "Alocado")
    #     total_atendentes = len(self.atendentes)
    #     total_senioridade = sum(a.senioridade_val for a in self.atendentes)
    #     total_valor_tickets = sum(t.valor_int for t in self.tickets if t.status == "Alocado")
    #     custo_total = sum(a.total_cost() for a in self.atendentes)
    #     tk.Label(self.frame_summary, text="RESUMO", font=("Helvetica", 14, "bold"), bg="white", fg="black").pack(pady=5)
    #     tk.Label(self.frame_summary, text=f"Total de Tickets: {total_tickets}", bg="white", fg="black").pack(anchor="w")
    #     tk.Label(self.frame_summary, text=f"Tickets Alocados: {tickets_alocados}", bg="white", fg="black").pack(anchor="w")
    #     tk.Label(self.frame_summary, text=f"Total de Atendentes: {total_atendentes}", bg="white", fg="black").pack(anchor="w")
    #     tk.Label(self.frame_summary, text=f"Total de Senioridade: {total_senioridade}", bg="white", fg="black").pack(anchor="w")
    #     tk.Label(self.frame_summary, text=f"Total de Valor (Tickets): {total_valor_tickets}", bg="white", fg="black").pack(anchor="w")
    #     tk.Label(self.frame_summary, text=f"Custo Total: R$ {custo_total:.2f}", bg="white", fg="black").pack(anchor="w")

    # Métodos de Drag & Drop para Tickets
    def on_ticket_press(self, event, ticket):
        self.drag_data = {"ticket": ticket, "ghost": None}
        ghost = ctk.CTkToplevel(self.root)
        ghost.overrideredirect(True)
        ghost.configure(fg_color="#d1c21b")
        label = ctk.CTkLabel(ghost, text=f"Ticket: {ticket.nome}", fg_color="#d1c21b", text_color="black")
        label.pack()
        self.drag_data["ghost"] = ghost
        ghost.geometry(f"+{event.x_root}+{event.y_root}")

    def on_ticket_motion(self, event):
        if self.drag_data.get("ghost"):
            ghost = self.drag_data["ghost"]
            ghost.geometry(f"+{event.x_root}+{event.y_root}")

    def on_ticket_release(self, event):
        if not self.drag_data:
            return
        ghost = self.drag_data.get("ghost")
        ticket = self.drag_data.get("ticket")
        if ghost and ticket:
            x, y = event.x_root, event.y_root
            allocated = False
            for atendente in self.atendentes:
                ax = atendente.widget.winfo_rootx()
                ay = atendente.widget.winfo_rooty()
                aw = atendente.widget.winfo_width()
                ah = atendente.widget.winfo_height()
                if (ax <= x <= ax + aw) and (ay <= y <= ay + ah):
                    if len(atendente.tickets_alocados) >= atendente.senioridade_val:
                        messagebox.showerror("Erro", "Este atendente já atingiu sua capacidade!")
                    else:
                        if ticket.atendente:
                            ticket.atendente.tickets_alocados.remove(ticket)
                        ticket.status = "Alocado"
                        ticket.atendente = atendente
                        atendente.tickets_alocados.append(ticket)
                        allocated = True
                    break
            ghost.destroy()
            self.drag_data = {}
            if allocated:
                self.atualizar_listas()

    # Métodos de Importação via CSV
    def importar_tickets(self):
        filename = askopenfilename(filetypes=[("CSV files", "*.csv")])
        if not filename:
            return
        with open(filename, newline="", encoding="utf-8") as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                nome = row.get("ticket_nome", "").strip()
                valor = row.get("ticket_value", "").strip()
                if any(t.nome.lower() == nome.lower() for t in self.tickets):
                    continue
                if nome and valor:
                    self.tickets.append(Ticket(nome, valor))
        self.atualizar_listas()

    def importar_atendentes(self):
        filename = askopenfilename(filetypes=[("CSV files", "*.csv")])
        if not filename:
            return
        with open(filename, newline="", encoding="utf-8") as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                nome = row.get("person_name", "").strip()
                capacidade = row.get("person_capacity", "").strip()
                custo = row.get("person_cost", "").strip()
                if any(a.nome.lower() == nome.lower() for a in self.atendentes):
                    continue
                if nome and capacidade and custo:
                    self.atendentes.append(Atendente(nome, capacidade, custo))
        self.atualizar_listas()

    def importar_alocacoes(self):
        """
        Importa alocações a partir de um CSV com colunas:
        ticket_nome, person_name
        """
        filename = askopenfilename(filetypes=[("CSV files", "*.csv")])
        if not filename:
            return
        with open(filename, newline="", encoding="utf-8") as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                ticket_nome = row.get("ticket_nome", "").strip()
                person_name = row.get("person_name", "").strip()
                ticket = next((t for t in self.tickets if t.nome.lower() == ticket_nome.lower()), None)
                atendente = next((a for a in self.atendentes if a.nome.lower() == person_name.lower()), None)
                if ticket and atendente:
                    if len(atendente.tickets_alocados) < atendente.senioridade_val:
                        if ticket.atendente:
                            ticket.atendente.tickets_alocados.remove(ticket)
                        ticket.status = "Alocado"
                        ticket.atendente = atendente
                        atendente.tickets_alocados.append(ticket)
        self.atualizar_listas()

    # Métodos para criação manual via janelas
    def janela_criar_ticket(self):
        janela = ctk.CTkToplevel(self.root)
        janela.title("Criar Ticket")
        janela.geometry("400x300")
        janela.configure(fg_color="white")

        janela.focus_force()  # Sets focus to the new window
        janela.attributes("-topmost", True)  # Forces window to stay on top
        janela.lift()  # Brings it to the front

        ctk.CTkLabel(janela, text="Nome do Ticket:", text_color="black", fg_color="white").pack(pady=5)
        entry_nome = ctk.CTkEntry(janela)
        entry_nome.pack()
        ctk.CTkLabel(janela, text="Valor do Ticket (ex: 10 ou R$10):", text_color="black", fg_color="white").pack(pady=5)
        entry_valor = ctk.CTkEntry(janela)
        entry_valor.pack()
        def salvar_ticket():
            nome = entry_nome.get().strip()
            valor_str = entry_valor.get().strip()
            if not nome or not valor_str:
                messagebox.showwarning("Atenção", "Preencha todos os campos.")
                return
            if any(t.nome.lower() == nome.lower() for t in self.tickets):
                messagebox.showerror("Erro", "Ticket com esse nome já existe!")
                return
            novo_ticket = Ticket(nome, valor_str)
            self.tickets.append(novo_ticket)
            self.atualizar_listas()
            janela.destroy()
        ctk.CTkButton(janela, text="Salvar", fg_color="#333",
                  command=salvar_ticket).pack(pady=10)

    def janela_criar_atendente(self):
        janela = ctk.CTkToplevel(self.root)
        janela.title("Criar Atendente")
        janela.geometry("450x300")
        janela.configure(fg_color="white")

        janela.focus_force()  
        janela.attributes("-topmost", True) 
        janela.lift()        

        ctk.CTkLabel(janela, text="Nome do Atendente:", text_color="black", fg_color="white").pack(pady=5)
        entry_nome = ctk.CTkEntry(janela)
        entry_nome.pack()
        ctk.CTkLabel(janela, text="Senioridade (número - capacidade):", text_color="black", fg_color="white").pack(pady=5)
        entry_senioridade = ctk.CTkEntry(janela)
        entry_senioridade.pack()
        ctk.CTkLabel(janela, text="Custo (ex: R$ 100/h):", text_color="black", fg_color="white").pack(pady=5)
        entry_custo = ctk.CTkEntry(janela)
        entry_custo.pack()
        def salvar_atendente():
            nome = entry_nome.get().strip()
            senioridade_str = entry_senioridade.get().strip()
            custo = entry_custo.get().strip()
            if not nome or not senioridade_str or not custo:
                messagebox.showwarning("Atenção", "Preencha todos os campos.")
                return
            if any(a.nome.lower() == nome.lower() for a in self.atendentes):
                messagebox.showerror("Erro", "Atendente com esse nome já existe!")
                return
            novo_atendente = Atendente(nome, senioridade_str, custo)
            self.atendentes.append(novo_atendente)
            self.atualizar_listas()
            janela.destroy()
        ctk.CTkButton(janela, text="Salvar", fg_color="#333",
                  command=salvar_atendente).pack(pady=10)

    def limpar_alocacoes(self):
        for ticket in self.tickets:
            ticket.status = "Não alocado"
            ticket.atendente = None
        for atendente in self.atendentes:
            atendente.tickets_alocados.clear()
        self.atualizar_listas()

    def limpar_tickets(self):
        self.tickets.clear()
        self.atualizar_listas()

    def limpar_atendentes(self):
        self.atendentes.clear()
        self.atualizar_listas()

def main():
    root = ctk.CTk()
    # Exemplo de dados estruturados (opcional)
    # tickets_data = [
    #     {"ticket_nome": "Ticket 1", "ticket_value": "10"},
    #     {"ticket_nome": "Ticket 2", "ticket_value": "15"},
    #     {"ticket_nome": "Ticket 3", "ticket_value": "20"},
    #     {"ticket_nome": "Ticket 4", "ticket_value": "25"}
    # ]
    # persons_data = [
    #     {"person_name": "Alice", "person_capacity": "20", "person_cost": "100"},
    #     {"person_name": "Bob", "person_capacity": "15", "person_cost": "80"},
    #     {"person_name": "Charlie", "person_capacity": "25", "person_cost": "120"},
    #     {"person_name": "Diana", "person_capacity": "30", "person_cost": "150"}
    # ]
    # alloc_data = [
    #     {"ticket_nome": "Ticket 1", "person_name": "Alice"}
    # ]
    # Instancia o app, passando os dados estruturados (ou caminhos de CSV, se preferir)
    # app = TicketManagerApp(root, tickets_data=tickets_data, persons_data=persons_data, alloc_data=alloc_data)
    app = TicketManagerApp(root)
    # Exemplo: passe os caminhos dos CSVs ao instanciar o aplicativo
    # app = TicketManagerApp(root,
    #                        tickets_csv="tickets.csv",
    #                        persons_csv="persons.csv",
    #                        allocations_csv="allocations.csv")
    root.mainloop()

if __name__ == "__main__":
    main()
