
import random
import math
import pandas as pd
from deap import base, creator, tools

class GeneticCode:
    def __init__(self, tarefas, profissionais, callback=None):
        self.tarefas = tarefas
        self.profissionais = profissionais
        self.callback = callback
        self.toolbox = base.Toolbox()

        if not hasattr(creator, "FitnessMin"):
            creator.create("FitnessMin", base.Fitness, weights=(-1.0, -1.0))
        if not hasattr(creator, "Individual"):
            creator.create("Individual", list, fitness=creator.FitnessMin)

        self.toolbox.register("individual", tools.initIterate, creator.Individual, self.create_individual)
        self.toolbox.register("population", tools.initRepeat, list, self.toolbox.individual)
        self.toolbox.register("evaluate", self.evaluate)
        self.toolbox.register("mate", tools.cxTwoPoint)
        self.toolbox.register("mutate", tools.mutUniformInt, low=0, up=len(profissionais) - 1, indpb=0.2)
        self.toolbox.register("select", tools.selNSGA2)

    def create_individual(self):
        return [random.randint(0, len(self.profissionais) - 1) for _ in range(len(self.tarefas))]

    def evaluate(self, individual):
        tempo_total_profissional = [0] * len(self.profissionais)
        custo_total = 0

        for i, prof_idx in enumerate(individual):
            prof = self.profissionais[prof_idx]
            tarefa = self.tarefas[i]
            tempo = tarefa["peso"] / prof["capacidade"] if prof["capacidade"] >= tarefa["peso"] else tarefa["peso"] / prof["capacidade"] * 2
            horas_faturadas = math.ceil(tempo)
            tempo_total_profissional[prof_idx] += tempo
            custo_total += horas_faturadas * prof["valor_hora"]

        tempo_processamento_total = max(tempo_total_profissional)
        penalizacao_custo = custo_total * 0.01
        penalizacao_tempo = tempo_processamento_total * 50

        custo_ajustado = custo_total + penalizacao_tempo
        tempo_ajustado = tempo_processamento_total + penalizacao_custo

        return custo_ajustado, tempo_ajustado

    def analyze_solution(self, solution):
        alocacao = []
        tempo_total_profissional = [0] * len(self.profissionais)

        for i, prof_idx in enumerate(solution):
            prof = self.profissionais[prof_idx]
            tarefa = self.tarefas[i]
            tempo = tarefa["peso"] / prof["capacidade"] if prof["capacidade"] >= tarefa["peso"] else tarefa["peso"] / prof["capacidade"] * 1.5
            horas_faturadas = math.ceil(tempo)
            custo = horas_faturadas * prof["valor_hora"]
            tempo_total_profissional[prof_idx] += tempo

            alocacao.append({
                "tarefa": tarefa["nome"],
                "profissional": prof["nome"],
                "valor": tarefa["peso"] * 10  # valor fictício
            })

        df_alocacao = pd.DataFrame(alocacao)
        tempo_processo = max(tempo_total_profissional)
        custo_total = df_alocacao["valor"].sum()
        return df_alocacao, tempo_processo, custo_total

    def execute(self, tamanho_pop=100, num_geracoes=40):
        pop = self.toolbox.population(n=tamanho_pop)
        fitnesses = list(map(self.toolbox.evaluate, pop))
        for ind, fit in zip(pop, fitnesses):
            ind.fitness.values = fit

        for gen in range(num_geracoes):
            offspring = self.toolbox.select(pop, len(pop))
            offspring = list(map(self.toolbox.clone, offspring))

            for child1, child2 in zip(offspring[::2], offspring[1::2]):
                if random.random() < 0.8:
                    self.toolbox.mate(child1, child2)
                    del child1.fitness.values
                    del child2.fitness.values

            for mutant in offspring:
                if random.random() < 0.1:
                    self.toolbox.mutate(mutant)
                    del mutant.fitness.values

            invalid_ind = [ind for ind in offspring if not ind.fitness.valid]
            fitnesses = map(self.toolbox.evaluate, invalid_ind)
            for ind, fit in zip(invalid_ind, fitnesses):
                ind.fitness.values = fit

            pop[:] = offspring

            best = tools.selBest(pop, 1)[0]
            if self.callback:
                df, tempo, custo = self.analyze_solution(best)
                self.callback(gen, df, tempo, custo)

        return tools.selBest(pop, 1)[0]
