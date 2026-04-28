import numpy as np


def tournament_selection(population, fitness_values, tournament_size=3):
    selected_indices = np.random.choice(len(population), tournament_size, replace=False)
    tournament_fitness = fitness_values[selected_indices]
    winner_index = selected_indices[np.argmax(tournament_fitness)]
    return population[winner_index].copy()


def roulette_wheel_selection(population, fitness_values):
    # Чтобы избежать отрицательных значений приспособленности
    min_fitness = np.min(fitness_values)
    if min_fitness < 0:
        fitness_values = fitness_values - min_fitness + 1e-5

    probabilities = fitness_values / np.sum(fitness_values)
    selected_index = np.random.choice(len(population), p=probabilities)
    return population[selected_index].copy()