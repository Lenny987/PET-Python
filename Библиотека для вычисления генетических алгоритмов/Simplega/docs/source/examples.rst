Examples
========

Basic Usage Examples
--------------------

Maximizing a Simple Function
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from simplega import GeneticAlgorithm
   import numpy as np

   def maximize_ones(individual):
       '''Maximize the number of ones in binary string'''
       return np.sum(individual)

   ga = GeneticAlgorithm(
       fitness_func=maximize_ones,
       population_size=50,
       gene_length=25,
       generations=100
   )

   best, fitness, history = ga.run()
   print(f"Best solution: {best}")
   print(f"Fitness: {fitness}")

Complex Optimization Problem
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   import math

   def complex_function(individual):
       '''Optimize a multi-modal function'''
       # Convert binary to float in range [0, 1]
       x = int(''.join(str(bit) for bit in individual[:8]), 2) / 255.0
       y = int(''.join(str(bit) for bit in individual[8:]), 2) / 255.0

       # Multi-modal function with multiple peaks
       result = (math.sin(10 * x) * math.cos(4 * y) -
                (x - 0.5)**2 - (y - 0.3)**2)
       return result

   ga = GeneticAlgorithm(
       fitness_func=complex_function,
       population_size=80,
       gene_length=16,  # 8 bits for x + 8 bits for y
       generations=150,
       mutation_rate=0.02
   )

Advanced Examples
-----------------

Custom Operators
~~~~~~~~~~~~~~~~

You can create custom genetic operators:

.. code-block:: python

   from simplega.operators import tournament_selection

   def my_custom_crossover(parent1, parent2):
       # Your custom crossover implementation
       point = len(parent1) // 2
       child1 = np.concatenate([parent1[:point], parent2[point:]])
       child2 = np.concatenate([parent2[:point], parent1[point:]])
       return child1, child2

Visualization
~~~~~~~~~~~~~

.. code-block:: python

   from simplega.visualization import plot_fitness

   # After running the algorithm
   plot_fitness(history, title="Algorithm Convergence")

   # Custom styling
   plot_fitness(
       history,
       title="My Optimization Results",
       figsize=(12, 6)
   )