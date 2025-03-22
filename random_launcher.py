# random_launcher.py

import tkinter as tk
import customtkinter as ctk
import random
from app import TicketManagerApp

def generate_random_tickets(num=5):
    """Gera uma lista de dicionários representando tickets aleatórios."""
    tickets = []
    for i in range(num):
        ticket_nome = f"Ticket {i+1}"
        valor = str(random.randint(10, 100))  # Valor entre 10 e 100
        tickets.append({"ticket_nome": ticket_nome, "ticket_value": valor})
    return tickets

def generate_random_persons(num=3):
    """Gera uma lista de dicionários representando atendentes aleatórios."""
    persons = []
    nomes_possiveis = base_names = [
    "rafael", "gabriel", "joao", "maria", "ana", "carlos", "paulo", "lucas", "pedro", "antonio",
    "rafaela", "juliana", "marcos", "roberto", "fernando", "ricardo", "eduardo", "andre", "felipe", "luana"
]
    random.shuffle(nomes_possiveis)
    for i in range(num):
        nome = nomes_possiveis[i % len(nomes_possiveis)]
        capacidade = str(random.randint(10, 30))  # Senioridade entre 10 e 30
        custo = str(random.randint(50, 200))      # Custo entre 50 e 200
        persons.append({
            "person_name": nome,
            "person_capacity": capacidade,
            "person_cost": custo
        })
    return persons

def generate_random_allocations(tickets, persons):
    """
    Gera alocações (ticket_nome, person_name) aleatórias, sem ultrapassar a capacidade.
    Exemplo simples: para cada ticket, escolhe um atendente aleatório.
    """
    allocations = []
    for t in tickets:
        person = random.choice(persons)
        allocations.append({
            "ticket_nome": t["ticket_nome"],
            "person_name": person["person_name"]
        })
    return allocations

def main():
    # Gera dados aleatórios
    tickets_data = generate_random_tickets(num=10)
    persons_data = generate_random_persons(num=10)
    alloc_data = generate_random_allocations(tickets_data, persons_data)

    # Cria a janela e passa os dados aleatórios
    root = ctk.CTk()
    app = TicketManagerApp(root,
                           tickets_data=tickets_data,
                           persons_data=persons_data,
                           alloc_data=alloc_data)
    app.atualizar_listas()
    root.mainloop()

if __name__ == "__main__":
    main()
