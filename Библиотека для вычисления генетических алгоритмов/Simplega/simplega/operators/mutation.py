import numpy as np

def bit_flip_mutation(individual, mutation_rate):
    mutated_individual = individual.copy()
    for i in range(len(mutated_individual)):
        if np.random.rand() < mutation_rate:
            mutated_individual[i] = 1 - mutated_individual[i]  # Инвертирование бита
    return mutated_individual

def swap_mutation(individual, mutation_rate):
    mutated_individual = individual.copy()
    if np.random.rand() < mutation_rate:
        idx1, idx2 = np.random.choice(len(individual), 2, replace=False)
        mutated_individual[idx1], mutated_individual[idx2] = mutated_individual[idx2], mutated_individual[idx1]
    return mutated_individual