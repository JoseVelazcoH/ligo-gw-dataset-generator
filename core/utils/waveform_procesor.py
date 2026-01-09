import numpy as np
from scipy import interpolate
from typing import Tuple, List

import core.constants.gw_constants as constants
from core.utils.logger import Logger

class WaveformProcessor:

    @staticmethod
    def resample_waveform(
        time: List[float],
        waveform: List[float],
        frequency: float
    ) -> Tuple[List[float], List[float]]:

        try:

            time = np.array(time)
            time_resampled = np.arange(time[0], time[-1], 1.0/frequency)

            spline_representation = interpolate.splrep(time, waveform, s=0)
            waveform_resampled = interpolate.splev(time_resampled, spline_representation, der=0)

            return time_resampled, waveform_resampled

        except ValueError as e:
            Logger.error(f"Value error: {e}")
            return None, None

        except Exception as e:
            Logger.error(f"Error in the interpolation {e}")
            return None, None

    @staticmethod
    def rescale_waveform_amplitude(
        waveform: List[float],
        distance: float
    )-> List[float]:

        try:
            rescaled_waveform = constants.default_kpc_distance * (waveform / distance)
            return rescaled_waveform
        except Exception as e:
            Logger.error(f"Error in amplitude rescaling: {e}")
            return None

    @staticmethod
    def waveform_to_dimensionless(
        waveform: List[float]
    )-> List[float]:

        return waveform * constants.cm2kpc
