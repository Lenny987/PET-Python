import numpy as np

def create_binary_population(population_size, gene_length):
    return np.random.randint(0, 2, (population_size, gene_length))

def binary_to_decimal(binary_array, min_val=0, max_val=10):
    decimal = int(''.join(str(bit) for bit in binary_array), 2)
    max_binary = 2 ** len(binary_array) - 1
    return min_val + (decimal / max_binary) * (max_val - min_val)