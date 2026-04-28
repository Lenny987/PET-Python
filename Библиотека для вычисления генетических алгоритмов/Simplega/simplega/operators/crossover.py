import numpy as np

def single_point_crossover(parent1, parent2):
    point = np.random.randint(1, len(parent1))
    child1 = np.concatenate((parent1[:point], parent2[point:]))
    child2 = np.concatenate((parent2[:point], parent1[point:]))
    return child1, child2

def two_point_crossover(parent1, parent2):
    point1, point2 = sorted(np.random.choice(range(1, len(parent1)), 2, replace=False))
    child1 = np.concatenate((parent1[:point1], parent2[point1:point2], parent1[point2:]))
    child2 = np.concatenate((parent2[:point1], parent1[point1:point2], parent2[point2:]))
    return child1, child2

def uniform_crossover(parent1, parent2, rate=0.5):
    mask = np.random.rand(len(parent1)) < rate
    child1 = np.where(mask, parent1, parent2)
    child2 = np.where(mask, parent2, parent1)
    return child1, child2