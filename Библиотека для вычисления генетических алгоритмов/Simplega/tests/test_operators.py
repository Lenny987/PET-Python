import pytest
import numpy as np
from Simplega.simplega.operators.selection import tournament_selection, roulette_wheel_selection
from Simplega.simplega.operators.crossover import single_point_crossover, two_point_crossover, uniform_crossover
from Simplega.simplega.operators.mutation import bit_flip_mutation, swap_mutation


class TestSelection:

    def test_tournament_selection(self):
        population = np.array([[1, 1, 1], [0, 0, 0], [1, 0, 1], [0, 1, 0]])
        fitness = np.array([3, 0, 2, 1])
        selected = tournament_selection(population, fitness, tournament_size=2)

        assert selected.shape == (3,)
        # Проверим, что selected находится в population
        assert any(np.array_equal(selected, ind) for ind in population)

    def test_roulette_wheel_selection(self):
        population = np.array([[1, 1, 1], [0, 0, 0], [1, 0, 1], [0, 1, 0]])
        fitness = np.array([3, 1, 2, 1])
        selected = roulette_wheel_selection(population, fitness)

        assert selected.shape == (3,)
        assert any(np.array_equal(selected, ind) for ind in population)


class TestCrossover:

    def test_single_point_crossover(self):
        parent1 = np.array([1, 1, 1, 1])
        parent2 = np.array([0, 0, 0, 0])
        child1, child2 = single_point_crossover(parent1, parent2)

        assert len(child1) == len(parent1)
        assert len(child2) == len(parent2)

    def test_two_point_crossover(self):
        parent1 = np.array([1, 1, 1, 1, 1])
        parent2 = np.array([0, 0, 0, 0, 0])
        child1, child2 = two_point_crossover(parent1, parent2)

        assert len(child1) == len(parent1)
        assert len(child2) == len(parent2)


class TestMutation:

    def test_bit_flip_mutation(self):
        individual = np.array([1, 1, 1, 1])
        mutated = bit_flip_mutation(individual, mutation_rate=1.0)
        expected = np.array([0, 0, 0, 0])

        assert np.array_equal(mutated, expected)

    def test_bit_flip_mutation_no_mutation(self):
        individual = np.array([1, 1, 1, 1])
        mutated = bit_flip_mutation(individual, mutation_rate=0.0)

        assert np.array_equal(mutated, individual)

    def test_swap_mutation(self):
        individual = np.array([1, 2, 3, 4])
        mutated = swap_mutation(individual, mutation_rate=1.0)

        # Должны поменяться местами два гена
        assert set(individual) == set(mutated)
        assert len(individual) == len(mutated)