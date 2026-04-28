import pytest
import numpy as np
from Simplega.simplega.core import GeneticAlgorithm


def test_initialization():

    def dummy_fitness(individual):
        return sum(individual)

    ga = GeneticAlgorithm(dummy_fitness, population_size=50, gene_length=10)

    assert ga.population_size == 50
    assert ga.gene_length == 10
    assert ga.generations == 100
    assert ga.crossover_rate == 0.8
    assert ga.mutation_rate == 0.1


def test_run_returns_best_solution():

    def simple_fitness(individual):
        return np.sum(individual)

    ga = GeneticAlgorithm(simple_fitness, population_size=10, gene_length=5, generations=10)
    best_solution, best_fitness, history = ga.run()

    assert best_solution is not None
    assert best_fitness >= 0
    assert 'best' in history
    assert 'avg' in history
    assert 'worst' in history
    assert len(history['best']) == 10


def test_population_creation():

    def dummy_fitness(individual):
        return sum(individual)

    ga = GeneticAlgorithm(dummy_fitness, population_size=20, gene_length=8)
    ga._create_population()

    assert ga.population.shape == (20, 8)
    assert np.all((ga.population >= 0) & (ga.population <= 1))