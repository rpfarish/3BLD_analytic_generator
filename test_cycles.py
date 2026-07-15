import random

 def random_cycle_lengths(total_targets=11, first_min=4, pseudoswap=True):
     """
     Generate cycle lengths without rejection.
 
     The first cycle is chosen uniformly from the allowed lengths.
     The remaining cycle lengths follow the exact distribution induced by
     a random permutation on the remaining elements.
     """
 
     n = total_targets - 1 if pseudoswap else total_targets
 
     # Choose the first cycle length directly.
     first = random.randint(first_min, n)

     cycles = [first]
     remaining = n - first
 
     while remaining:
         # The cycle containing the smallest remaining element has
         # uniform length on {1,...,remaining}.
         k = random.randint(1, remaining)
         cycles.append(k)
         remaining -= k
     
     return cycles
