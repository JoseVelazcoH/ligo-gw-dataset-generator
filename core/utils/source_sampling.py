import math
from core.utils.validators import enforce_arguments

@enforce_arguments(choices ={'frequency': (4_096, 16_000)})
def get_sources_per_sample(
        n_samples: int,
        frequency: int = 4_096
        ) -> int:
    n_samples = n_samples + 2 # after procesing we remove 2 samples
    return math.ceil(n_samples/ frequency)
