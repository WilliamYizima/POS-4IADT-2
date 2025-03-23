## Participantes

Rafael Alves Cardoso -
RM 360124

Silvio Cezer Saczuck -
RM 360204

Luciano Giles Soares -
RM 359834

William Judice Yizima -
RM 360214

Luiz Ricardo Zinsly Calmon -
RM359894

## Entrega 02

# Problema Inicial

O contexto do problema é um ambiente de atendimento, onde existem tickets e atendentes com diferentes capacidades e custos.
<b>Queremos encontrar a melhor forma de alocar os tickets, minimizando o custo e tempo de entrega.</b>

Sobre o problema:

- Cada atendente tem um nome, uma senioridade(capacidade de entrega) e custo por hora
- Cada ticket tem um nome, um valor de dificuldade(que será relacionado com a capacidade de entrega do atendente)
- Neste caso, não vamos abordar 2 atendentes tratando o mesmo ticket

---

Dito isso podemos visualizar:

- Atendente:

  - Nome
  - Capacidade
  - R$/hora

- Ticket:
  - nome
  - Valor de dificuldade

### Cálculo do custo:

- custo = "tempo gasto" x "R$/hora do atendente"
- tempo gasto = "Valor de dificuldade do ticket" / "Capacidade do Atendente"
- Valor de dificuldade do ticket = Dado inicial do Ticket
- Capacidade do Atendente = Valor inicial do Atendente

Cálculo do tempo: - Somatório do "tempo gasto" de todos os atendentes

## Desafio com Algoritmo genético

Descobrir os valores de Hora Gasta e Custo distribuindo os tickets de forma otimizada.
Buscamos um equilíbrio entre Custo e Tempo, visando o melhor Custo Benefício

## Rodar

```
pip install -r requirements.txt
python main.py
```

irá abrir uma nova tela do tkinter para rodar
