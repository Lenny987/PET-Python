import matplotlib.pyplot as plt

def plot_fitness(fitness_history, title="График сходимости генетического алгоритма", figsize=(10, 6)):

    generations = range(1, len(fitness_history['best']) + 1)

    plt.figure(figsize=figsize)
    plt.plot(generations, fitness_history['best'], label='Лучшая', linewidth=2)
    plt.plot(generations, fitness_history['avg'], label='Средняя', linestyle='--')
    plt.plot(generations, fitness_history['worst'], label='Худшая', linestyle=':')

    plt.title(title)
    plt.xlabel('Поколение')
    plt.ylabel('Приспособленность')
    plt.legend()
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.show()