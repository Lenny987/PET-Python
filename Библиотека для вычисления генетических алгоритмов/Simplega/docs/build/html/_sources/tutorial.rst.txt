Tutorial
========

Quick Start
-----------

Here's a minimal example of using the library:

.. code-block:: python

   from simplega import GeneticAlgorithm
   from simplega.visualization import plot_fitness
   import numpy as np

   # Define a fitness function
   def fitness_func(individual):
       return np.sum(individual)

   # Create genetic algorithm
   ga = GeneticAlgorithm(
       fitness_func=fitness_func,
       population_size=50,
       gene_length=20,
       generations=100
   )

   # Run evolution
   best_solution, best_fitness, history = ga.run()

   # Visualize results
   plot_fitness(history)

Basic Concepts
--------------

Genetic Algorithm Components
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* **Population**: Collection of potential solutions
* **Fitness Function**: Evaluates quality of each solution
* **Selection**: Chooses parents for reproduction
* **Crossover**: Combines genetic material from parents
* **Mutation**: Introduces random changes

Configuration Options
~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   ga = GeneticAlgorithm(
       fitness_func=my_function,
       population_size=100,      # Size of population
       gene_length=30,           # Length of individual's genome
       generations=200,          # Number of evolutionary generations
       crossover_rate=0.8,       # Probability of crossover
       mutation_rate=0.05,       # Probability of mutation
       selection_type='tournament',  # 'tournament' or 'roulette'
       crossover_type='single_point', # 'single_point', 'two_point', 'uniform'
       mutation_type='bit_flip'  # 'bit_flip' or 'swap'
   )