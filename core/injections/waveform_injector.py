import numpy as np
from pycbc.types import TimeSeries
from pycbc.filter import sigma
from pycbc.psd import welch, interpolate
from typing import List, Tuple
from numpy.typing import NDArray

from core.types.custom_types import InjectionInfo
from core.utils.logger import Logger


class WaveformInjector:

    SNR_CALCULATION_WINDOW_SECONDS: float = 4.0

    @staticmethod
    def inject_waveforms(
        strain_noise: NDArray[np.float64],
        waveform: NDArray[np.float64],
        injection_interval_seconds: float,
        sampling_frequency: float,
        sample_duration_seconds: float,
        n_injections: int = None,
        use_first_half: bool = True
    ) -> Tuple[NDArray[np.float64], List[InjectionInfo]]:

        if use_first_half:
            Logger.warning("Using only first half of strain for injections")
        else:
            Logger.warning("Using entire strain for injections")

        strain_injected = np.copy(strain_noise)
        injection_positions = WaveformInjector._calculate_injection_positions(
            strain_length=len(strain_noise),
            injection_interval_seconds=injection_interval_seconds,
            sampling_frequency=sampling_frequency,
            use_first_half=use_first_half
        )

        if n_injections is not None:
            injection_positions = injection_positions[:n_injections]

        if len(injection_positions) == 0:
            Logger.info("No injections performed due to insufficient strain length")
            return strain_injected, []

        half_window_samples = int((WaveformInjector.SNR_CALCULATION_WINDOW_SECONDS / sample_duration_seconds) * 0.5)

        Logger.info(f"First injection at sample: {injection_positions[0]}", verbose=False)
        Logger.info(f"Number of injections to perform: {len(injection_positions)}")

        injection_log: List[InjectionInfo] = []

        for idx, sample_index in enumerate(injection_positions):
            Logger.info(f"Injection No. {idx + 1}", verbose=False)

            injection_time_seconds = sample_index / sampling_frequency
            Logger.info(f"Time injection: {injection_time_seconds:.4f}s", verbose=False)

            start_index = sample_index
            end_index = sample_index + len(waveform)
            strain_injected[start_index:end_index] += waveform

            snr = WaveformInjector._compute_injection_snr(
                strain_injected=strain_injected,
                waveform=waveform,
                injection_sample_index=sample_index,
                half_window_samples=half_window_samples,
                sample_duration_seconds=sample_duration_seconds
            )

            Logger.info(f"Injection SNR value: {snr:.4f}", verbose=False)

            waveform_duration_seconds = len(waveform) * sample_duration_seconds

            injection_log.append({
                "time_inj": injection_time_seconds,
                "snr": snr,
                "waveform_duration": waveform_duration_seconds
            })

        Logger.info(f"Completed {len(injection_positions)} injections")

        return strain_injected, injection_log

    @staticmethod
    def _calculate_injection_positions(
        strain_length: int,
        injection_interval_seconds: float,
        sampling_frequency: float,
        use_first_half: bool = True
    ) -> NDArray[np.int64]:
        samples_per_interval = int(injection_interval_seconds * sampling_frequency)
        if samples_per_interval == 0:
            return np.array([], dtype=np.int64)

        max_possible_injections = strain_length // samples_per_interval

        if use_first_half:
            num_injections = int(max_possible_injections * 0.5)
        else:
            num_injections = max_possible_injections

        if num_injections == 0:
            return np.array([], dtype=np.int64)

        positions = np.arange(1, num_injections + 1) * samples_per_interval
        return positions.astype(np.int64)

    @staticmethod
    def _compute_injection_snr(
        strain_injected: NDArray[np.float64],
        waveform: NDArray[np.float64],
        injection_sample_index: int,
        half_window_samples: int,
        sample_duration_seconds: float
    ) -> float:
        left_limit = max(0, injection_sample_index - half_window_samples)
        right_limit = injection_sample_index + len(waveform) + half_window_samples
        noise_segment_with_signal = strain_injected[left_limit:right_limit]

        return WaveformInjector.calculate_snr(
            waveform=waveform,
            noise_segment=noise_segment_with_signal,
            sample_duration_seconds=sample_duration_seconds
        )

    @staticmethod
    def calculate_snr(
        waveform: NDArray[np.float64],
        noise_segment: NDArray[np.float64],
        sample_duration_seconds: float
    ) -> float:
        if len(noise_segment) < len(waveform):
            Logger.warning(f"waveform lenght: {len(waveform)}> noise_segment: {len(noise_segment)}")
            Logger.warning(f"Returning snr = {0.0}")
            return 0.0

        noise_timeseries = TimeSeries(noise_segment, delta_t=sample_duration_seconds)
        waveform_timeseries = TimeSeries(waveform, delta_t=sample_duration_seconds)

        sampling_frequency = 1.0 / sample_duration_seconds
        segment_length = int(4 * sampling_frequency)
        segment_stride = int(2 * sampling_frequency)

        if len(noise_timeseries) < segment_length:
            return 0.0

        psd = welch(noise_timeseries, seg_len=segment_length, seg_stride=segment_stride)
        delta_f = 1.0 / len(waveform_timeseries) * sampling_frequency
        psd = interpolate(psd, delta_f)

        snr_value = sigma(waveform_timeseries, psd=psd, low_frequency_cutoff=1.0)
        return float(snr_value)
