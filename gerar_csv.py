import csv

# Lista de tickets (cada dicionário tem as chaves 'ticket_nome' e 'ticket_value')
tickets = [
    {"ticket_nome": "Ticket 1", "ticket_value": "10"},
    {"ticket_nome": "Ticket 2", "ticket_value": "15"},
    {"ticket_nome": "Ticket 3", "ticket_value": "20"},
    {"ticket_nome": "Ticket 4", "ticket_value": "25"}
]

# Lista de pessoas/atendentes (cada dicionário tem as chaves 'person_name', 'person_capacity' e 'person_cost')
persons = [
    {"person_name": "Alice", "person_capacity": "20", "person_cost": "100"},
    {"person_name": "Bob", "person_capacity": "15", "person_cost": "80"},
    {"person_name": "Charlie", "person_capacity": "25", "person_cost": "120"},
    {"person_name": "Diana", "person_capacity": "30", "person_cost": "150"}
]

# Cria o CSV para tickets
with open("tickets.csv", "w", newline="", encoding="utf-8") as csvfile:
    fieldnames = ["ticket_nome", "ticket_value"]
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    for ticket in tickets:
        writer.writerow(ticket)

# Cria o CSV para atendentes/pessoas
with open("persons.csv", "w", newline="", encoding="utf-8") as csvfile:
    fieldnames = ["person_name", "person_capacity", "person_cost"]
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    for person in persons:
        writer.writerow(person)

# Cria o CSV para alocações
# Neste exemplo, vamos alocar os tickets para os atendentes correspondentes (primeiro com primeiro, etc.)
allocations = []
for ticket, person in zip(tickets, persons):
    allocations.append({
        "ticket_nome": ticket["ticket_nome"],
        "person_name": person["person_name"]
    })

with open("allocations.csv", "w", newline="", encoding="utf-8") as csvfile:
    fieldnames = ["ticket_nome", "person_name"]
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    for alloc in allocations:
        writer.writerow(alloc)

print("Arquivos CSV 'tickets.csv', 'persons.csv' e 'allocations.csv' criados com sucesso!")
