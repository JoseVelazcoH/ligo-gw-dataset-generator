from typing import TypedDict, Dict, List, TYPE_CHECKING
from numpy.typing import NDArray
import numpy as np

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


class WaveformData(TypedDict):
    time: NDArray[np.float64]
    h_plus: NDArray[np.float64]
    h_cross: NDArray[np.float64]


class InjectionLoaderData(TypedDict):
    strain: LoaderData
    waveform: WaveformData


class ProcessedNoiseData(TypedDict):
    strain: "pycbc.types.TimeSeries"
    time: NDArray[np.float64]
    psd: "pycbc.types.frequencyseries.FrequencySeries"
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


class InjectionInfo(TypedDict):
    time_inj: float
    snr: float
    waveform_duration: float


class InjectionWindowedSample(TypedDict):
    time: NDArray[np.float64]
    strain: NDArray[np.float64]
    sample_index: int
    file_index: int
    detector: str
    gps_start: float
    distance: float
    snr: float
    injection_time: float


InjectionTransformerData = Dict[float, List[InjectionWindowedSample]]
