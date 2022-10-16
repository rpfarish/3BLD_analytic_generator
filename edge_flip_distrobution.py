from random import choices

population = list(range(0, 7))
weights = [0.6318, 0.2907, 0.0664, 0.0099, 0.0011, 0.00009, 0.00001]
num_of_flips = choices(population, weights)
print(num_of_flips)

million_samples = choices(population, weights, k=505440)
from collections import Counter

Counter(million_samples)
print(Counter(million_samples))
