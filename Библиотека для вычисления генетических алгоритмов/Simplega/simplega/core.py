import numpy as np
from .operators.selection import tournament_selection, roulette_wheel_selection
from .operators.crossover import single_point_crossover, two_point_crossover, uniform_crossover
from .operators.mutation import bit_flip_mutation, swap_mutation


class GeneticAlgorithm:

    def __init__(self, fitness_func, population_size=100, gene_length=10,
                 generations=100, crossover_rate=0.8, mutation_rate=0.1,
                 selection_type='tournament', crossover_type='single_point',
                 mutation_type='bit_flip'):

        self.fitness_func = fitness_func
        self.population_size = population_size
        self.gene_length = gene_length
        self.generations = generations
        self.crossover_rate = crossover_rate
        self.mutation_rate = mutation_rate
        self.selection_type = selection_type
        self.crossover_type = crossover_type
        self.mutation_type = mutation_type

        self.population = None
        self.fitness_history = {
            'best': [],
            'avg': [],
            'worst': []
        }

    def _create_population(self):
        self.population = np.random.randint(0, 2, (self.population_size, self.gene_length))

    def _calculate_fitness(self):
        return np.array([self.fitness_func(individual) for individual in self.population])

    def run(self):
        # Инициализация популяции
        self._create_population()
        best_individual = None
        best_fitness = -np.inf

        for gen in range(self.generations):
            # Вычисление приспособленности
            fitness_values = self._calculate_fitness()

            # Обновление истории
            current_best_fitness = np.max(fitness_values)
            current_avg_fitness = np.mean(fitness_values)
            current_worst_fitness = np.min(fitness_values)

            self.fitness_history['best'].append(current_best_fitness)
            self.fitness_history['avg'].append(current_avg_fitness)
            self.fitness_history['worst'].append(current_worst_fitness)

            # Обновление лучшего решения
            if current_best_fitness > best_fitness:
                best_fitness = current_best_fitness
                best_individual = self.population[np.argmax(fitness_values)].copy()

            # Создание новой популяции
            new_population = []
            for _ in range(self.population_size // 2):
                # Отбор родителей
                parent1 = self._select(fitness_values)
                parent2 = self._select(fitness_values)

                # Скрещивание
                if np.random.rand() < self.crossover_rate:
                    child1, child2 = self._crossover(parent1, parent2)
                else:
                    child1, child2 = parent1.copy(), parent2.copy()

                # Мутация
                child1 = self._mutate(child1)
                child2 = self._mutate(child2)

                new_population.extend([child1, child2])

            # Если population_size нечетный, добавляем одну особь
            if len(new_population) < self.population_size:
                new_population.append(new_population[0].copy())

            self.population = np.array(new_population)

        return best_individual, best_fitness, self.fitness_history

    def _select(self, fitness_values):
        if self.selection_type == 'tournament':
            return tournament_selection(self.population, fitness_values, tournament_size=3)
        elif self.selection_type == 'roulette':
            return roulette_wheel_selection(self.population, fitness_values)
        else:
            raise ValueError(f"Неизвестный тип отбора: {self.selection_type}")

    def _crossover(self, parent1, parent2):
        if self.crossover_type == 'single_point':
            return single_point_crossover(parent1, parent2)
        elif self.crossover_type == 'two_point':
            return two_point_crossover(parent1, parent2)
        elif self.crossover_type == 'uniform':
            return uniform_crossover(parent1, parent2)
        else:
            raise ValueError(f"Неизвестный тип скрещивания: {self.crossover_type}")

    def _mutate(self, individual):
        if self.mutation_type == 'bit_flip':
            return bit_flip_mutation(individual, self.mutation_rate)
        elif self.mutation_type == 'swap':
            return swap_mutation(individual, self.mutation_rate)
        else:
            raise ValueError(f"Неизвестный тип мутации: {self.mutation_type}")