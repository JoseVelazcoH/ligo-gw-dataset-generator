from typing import TypedDict, Dict, List, Tuple, TYPE_CHECKING
from numpy.typing import NDArray
import numpy as np
import pycbc

if TYPE_CHECKING:
    import pycbc.types
    import pycbc.types.frequencyseries

class GWOSCFileData(TypedDict):
    strain: NDArray[np.float64]
    gps_start: float
    duration: float
    time_sampling: float
    delta_t: float

LoaderData = Dict[str, Dict[int, GWOSCFileData]]
DetectorData = Dict[int, GWOSCFileData]

class ProcessedNoiseData(TypedDict):
    strain: pycbc.types.TimeSeries
    time: NDArray[np.float64]
    psd: pycbc.types.frequencyseries.FrequencySeries
    detector: str
    gps_start: float

class WindowedSample(TypedDict):
    time: NDArray[np.float64]
    strain: NDArray[np.float64]
    sample_index: int
    file_index: int
    detector: str
    gps_start: float

TransformerData = List[WindowedSample]
ExporterData = None
