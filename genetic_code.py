
import random
import math
import numpy as np
import pandas as pd
from deap import base, creator, tools

class GeneticCode:
    def __init__(self, tarefas, profissionais, callback=None):
        self.tarefas = tarefas
        self.profissionais = profissionais
        self.callback = callback
        self.toolbox = base.Toolbox()
        self.historico_populacoes = []
        self.historico_fitness = []

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
                "peso_tarefa": tarefa["peso"],
                "profissional": prof["nome"],
                "capacidade": prof["capacidade"],
                "tempo_estimado": round(tempo, 2),
                "horas_faturadas": horas_faturadas,
                "custo": custo
            })
        # Organiza os resultados
        df_alocacao = pd.DataFrame(alocacao)
        tempo_processo = max(tempo_total_profissional)
        custo_total = df_alocacao["custo"].sum()

        # Carga de trabalho por profissional
        carga_trabalho = []
        for i, tempo in enumerate(tempo_total_profissional):
            if tempo > 0:  # Só mostra profissionais com tarefas alocadas
                carga_trabalho.append({
                    "profissional": self.profissionais[i]["nome"],
                    "tempo_total": round(tempo, 2),
                    "tarefas": len([x for x in solution if x == i])
                })

        df_carga = pd.DataFrame(carga_trabalho)
        return df_alocacao,df_carga, tempo_processo, custo_total

    def execute(self, tamanho_pop=1000, num_geracoes=100):
        pop = self.toolbox.population(n=tamanho_pop)
        hof = tools.ParetoFront()  # Armazena as soluções não-dominadas
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
            # Avaliação
            invalid_ind = [ind for ind in offspring if not ind.fitness.valid]
            fitnesses = map(self.toolbox.evaluate, invalid_ind)
            for ind, fit in zip(invalid_ind, fitnesses):
                ind.fitness.values = fit

            # Atualização da população
            pop[:] = offspring

            # Atualiza o hall of fame
            hof.update(pop)

            # Armazenar para histórico
            self.historico_populacoes.append(pop[:])
            self.historico_fitness.append([ind.fitness.values for ind in pop])

            # Estatísticas da geração atual
            fits = [ind.fitness.values for ind in pop]
            min_fit = np.min(fits, axis=0)
            avg_fit = np.mean(fits, axis=0)

            # Exibe progresso
            print(f"-- Geração {gen+1} --")
            print(f"  Min: {min_fit}")
            print(f"  Avg: {avg_fit}")

        # Seleciona as melhores soluções
        # 1. Melhor equilíbrio (70% custo, 30% tempo)
        # pesos = (0.7, 0.3)
        # indice_equilibrio = np.argmin([pesos[0]*ind.fitness.values[0] + pesos[1]*ind.fitness.values[1] for ind in pop])

        # # 2. Menor custo
        # indice_menor_custo = np.argmin([ind.fitness.values[0] for ind in pop])

        # # 3. Menor tempo
        # indice_menor_tempo = np.argmin([ind.fitness.values[1] for ind in pop])

        # solucao_equilibrada = pop[indice_equilibrio]
        # solucao_menor_custo = pop[indice_menor_custo]
        # solucao_menor_tempo = pop[indice_menor_tempo]

        # return (solucao_equilibrada,
        #         solucao_menor_custo,
        #         solucao_menor_tempo,
        #         hof,
        #         self.historico_populacoes,
        #         self.historico_fitness)

            invalid_ind = [ind for ind in offspring if not ind.fitness.valid]
            fitnesses = map(self.toolbox.evaluate, invalid_ind)
            for ind, fit in zip(invalid_ind, fitnesses):
                ind.fitness.values = fit

            pop[:] = offspring

            best = tools.selBest(pop, 1)[0]
                # Seleciona as melhores soluções
            # 1. Melhor equilíbrio (70% custo, 30% tempo)
            pesos = (0.7, 0.3)
            indice_equilibrio = np.argmin([pesos[0]*ind.fitness.values[0] + pesos[1]*ind.fitness.values[1] for ind in pop])

            # 2. Menor custo
            indice_menor_custo = np.argmin([ind.fitness.values[0] for ind in pop])

            # 3. Menor tempo
            indice_menor_tempo = np.argmin([ind.fitness.values[1] for ind in pop])

            solucao_equilibrada = pop[indice_equilibrio]
            solucao_menor_custo = pop[indice_menor_custo]
            solucao_menor_tempo = pop[indice_menor_tempo]
            if self.callback:
                df, df_carga,tempo,custo = self.analyze_solution(solucao_equilibrada)
                print('>>>tempo e custo')
                print(custo)
                print(tempo)
                self.callback(gen, df, tempo, custo)

        return tools.selBest(pop, 1)[0]
