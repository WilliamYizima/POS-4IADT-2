
import tkinter as tk
from genetic_code import GeneticCode
import matplotlib.pyplot as plt

tarefas = [
    {"nome": f"Ticket {i+1}", "peso": p} for i, p in enumerate([2, 5, 3, 4, 7, 6, 9, 3, 4, 8])
]

profissionais = [
    {"nome": "felipe", "capacidade": 2, "valor_hora": 100},
    {"nome": "paulo", "capacidade": 3, "valor_hora": 110},
    {"nome": "joao", "capacidade": 4, "valor_hora": 120},
    {"nome": "gabriel", "capacidade": 5, "valor_hora": 130},
    {"nome": "pedro", "capacidade": 6, "valor_hora": 140},
]

alocacoes = {}
historico_fitness = []

def callback_por_geracao(gen, df_aloc, tempo, custo):
    global alocacoes, historico_fitness
    alocacoes.clear()
    for _, row in df_aloc.iterrows():
        alocacoes[row["tarefa"]] = row["profissional"]
    print('atualizando')
    atualizar_canvas()
    print('atualizei')
    resumo_var.set(f"Geração {gen+1}\nTickets: {len(tarefas)}\nAlocados: {len(alocacoes)}\nTempo: {tempo:.2f}h\nCusto: R$ {custo:.2f}")
    root.update_idletasks()
    root.after(200)

def rodar_algoritmo():
    global historico_fitness
    resumo_var.set("Executando algoritmo genético...")
    root.update_idletasks()
    historico_fitness = []
    gen = GeneticCode(tarefas, profissionais, callback=registrar_fitness)
    melhor = gen.execute()
    df_final, tempo, custo = gen.analyze_solution(melhor)
    callback_por_geracao(len(historico_fitness)-1, df_final, tempo, custo)
    visualizar_evolucao(historico_fitness)
    mostrar_metrica_final(tempo, custo)

def registrar_fitness(gen, df_aloc, tempo, custo):
    custos = [row["valor"] for _, row in df_aloc.iterrows()]
    tempos = [tempo for _ in custos]
    historico_fitness.append(list(zip(custos, tempos)))
    callback_por_geracao(gen, df_aloc, tempo, custo)

def atualizar_canvas():
    canvas.delete("all")
    for i, tarefa in enumerate(tarefas):
        y = 50 + i * 40
        canvas.create_rectangle(20, y, 160, y+30, fill="gray", outline="black")
        canvas.create_text(90, y+15, text=tarefa["nome"], fill="black")

    for j, prof in enumerate(profissionais):
        y = 50 + j * 80
        canvas.create_rectangle(440, y, 580, y+30, fill="lightyellow", outline="black")
        texto = f"{prof['nome']} ({prof['capacidade']})"
        canvas.create_text(510, y+15, text=texto, fill="black")

    for i, tarefa in enumerate(tarefas):
        nome_ticket = tarefa["nome"]
        if nome_ticket in alocacoes:
            atendente_nome = alocacoes[nome_ticket]
            t_y = 50 + i * 40
            a_index = next((j for j, a in enumerate(profissionais) if a["nome"] == atendente_nome), 0)
            a_y = 50 + a_index * 80
            canvas.create_line(160, t_y+15, 440, a_y+15, fill="black", width=2)

def visualizar_evolucao(historico_fitness):
    geracoes = range(len(historico_fitness))
    melhor_custo, media_custo = [], []
    melhor_tempo, media_tempo = [], []

    for gen in historico_fitness:
        custos = [f[0] for f in gen]
        tempos = [f[1] for f in gen]
        melhor_custo.append(min(custos))
        media_custo.append(sum(custos)/len(custos))
        melhor_tempo.append(min(tempos))
        media_tempo.append(sum(tempos)/len(tempos))

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))
    ax1.plot(geracoes, melhor_custo, 'r-', label='Melhor Custo')
    ax1.plot(geracoes, media_custo, 'r--', label='Média Custo')
    ax1.set_title('Evolução do Custo ao Longo das Gerações')
    ax1.set_xlabel('Geração')
    ax1.set_ylabel('Custo')
    ax1.legend()
    ax1.grid(True)

    ax2.plot(geracoes, melhor_tempo, 'b-', label='Melhor Tempo')
    ax2.plot(geracoes, media_tempo, 'b--', label='Média Tempo')
    ax2.set_title('Evolução do Tempo ao Longo das Gerações')
    ax2.set_xlabel('Geração')
    ax2.set_ylabel('Tempo')
    ax2.legend()
    ax2.grid(True)

    plt.tight_layout()
    plt.show()

def mostrar_metrica_final(tempo, custo):
    top = tk.Toplevel(root)
    top.title("Métricas Finais")
    top.configure(bg="lightgreen")
    msg = f"🏁 Resultado Final:\n\nTempo Total: {tempo:.2f} horas\nCusto Total: R$ {custo:.2f}"
    tk.Label(top, text=msg, bg="lightgreen", fg="black", font=("Arial", 14, "bold"), justify="center").pack(padx=20, pady=20)

root = tk.Tk()
root.title("Alocação com Algoritmo Genético")

canvas = tk.Canvas(root, width=600, height=500, bg="white")
canvas.grid(row=0, column=0, columnspan=3, padx=10, pady=10)

frame_resumo = tk.Frame(root, bg="lightgreen", bd=2, relief="groove")
frame_resumo.grid(row=1, column=0, padx=10, pady=10, sticky="w")
tk.Label(frame_resumo, text="RESUMO", bg="lightgreen", fg="black", font=("Arial", 12, "bold")).pack(pady=5)
resumo_var = tk.StringVar()
tk.Label(frame_resumo, textvariable=resumo_var, bg="lightgreen", fg="black", justify="left").pack()
tk.Button(frame_resumo, text="Rodar Algoritmo", command=rodar_algoritmo, bg="white", fg="black").pack(pady=10)

root.mainloop()
