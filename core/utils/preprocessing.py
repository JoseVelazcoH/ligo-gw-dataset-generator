
from pycbc.types.timeseries import TimeSeries
from pycbc.psd import welch as psd_welch
from pycbc.filter import highpass, lowpass_fir
from typing import List, Tuple

from core.utils.logger import Logger

class Preprocessing():

    @staticmethod
    def whitening(
            strain_data:List[float],
            lowpass_cutoff: int,
            whitening_window: float,
            delta_t: List
        ):
        Logger.info("Converting strain data to TimeSeries for whitening.", verbose=False)
        strain_timeseries = TimeSeries(strain_data, delta_t)
        whitened_strain, _ = strain_timeseries.whiten(whitening_window, lowpass_cutoff, return_psd=True)

        segment_length = int(4/delta_t)
        segment_stride = int(2/delta_t)
        Logger.info("Calculating PSD.", verbose=False)
        psd = psd_welch(strain_timeseries, seg_len=segment_length, seg_stride=segment_stride)
        psd_sqrt = psd**0.5
        scaling_factor = min(psd_sqrt)
        whitened_scaled = whitened_strain * scaling_factor

        psd_whitened_scaled = psd_welch(whitened_scaled, seg_len=segment_length, seg_stride=segment_stride)
        frequencies = psd.sample_frequencies

        return (whitened_scaled, psd_whitened_scaled, psd, frequencies)

    @staticmethod
    def bandpass(
        strain: List[float],
        lowcut: int,
        highcut: int,
        delta_t: list,
        order: int = 8
    ) -> Tuple[List[float], List[float]]:

        segment_length = int(4/delta_t)
        segment_stride = int(2/delta_t)

        strain_filtered = highpass(strain, lowcut, filter_order=order)
        strain_filtered = lowpass_fir(strain_filtered, highcut, order=order)
        psd_filtered = psd_welch(strain_filtered, segment_length, segment_stride)

        return (strain_filtered, psd_filtered)
