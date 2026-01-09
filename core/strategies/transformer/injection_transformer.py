import numpy as np
from typing import List, Dict
from dataclasses import dataclass

from core.strategies.base.transformer import TransformerBase
from core.types import InjectionLoaderData, InjectionTransformerData, InjectionWindowedSample
from core.utils.logger import Logger
from core.utils.preprocessing import whitening, bandpass
from core.utils.waveform_procesor import resample_waveform, rescale_waveform_amplitude, waveform_to_dimensionless
from core.injections.waveform_injector import WaveformInjector

@dataclass
class InjectionTransformer(TransformerBase):
    distances: List[float]
    detectors: List[str] = None
    injection_interval_seconds: float = 2.0
    window_size: float = 1.0
    whitening_cut: int = 10
    whitening_window: float = 0.5
    bandpass_fmin: float = 100.0
    bandpass_fmax: float = 1600.0
    n_samples: int = 1
    polarization: str = "h_plus"
    use_first_half: bool = True

    def transform(self, data: InjectionLoaderData, **kwargs) -> InjectionTransformerData:
        strain_data = data["strain"]
        waveform_data = data["waveform"]

        time_wf = waveform_data["time"]
        waveform_raw = waveform_data[self.polarization]

        waveform_duration = time_wf[-1] - time_wf[0]
        if self.window_size <= waveform_duration:
            raise ValueError(
                f"window_size ({self.window_size}s) must be greater than "
                f"waveform_duration ({waveform_duration:.4f}s)"
            )

        Logger.info("Converting waveform to dimensionless")
        waveform_dimensionless = waveform_to_dimensionless(waveform_raw)

        all_samples_by_distance: InjectionTransformerData = {distance: [] for distance in self.distances}

        for distance in self.distances:
            Logger.info(f"Processing injections at distance: {distance} kpc")

            waveform_rescaled = rescale_waveform_amplitude(
                waveform_dimensionless,
                distance
            )

            for detector in self.detectors:
                if detector not in strain_data:
                    Logger.warning(f"Detector {detector} not found in loaded data, skipping")
                    continue

                Logger.info(f"Processing detector {detector} at {distance} kpc")
                detector_files = strain_data[detector]
                detector_samples = []

                for file_index, file_data in detector_files.items():
                    if len(detector_samples) >= self.n_samples:
                        break

                    Logger.info(f"Processing file {file_index + 1}/{len(detector_files)}", verbose=False)

                    strain = file_data["strain"]
                    sample_duration_seconds = file_data["time_sampling"]
                    gps_start = file_data["gps_start"]
                    sampling_frequency = 1.0 / sample_duration_seconds

                    n_injections_possible = len(
                        WaveformInjector._calculate_injection_positions(
                            strain_length=len(strain),
                            injection_interval_seconds=self.injection_interval_seconds,
                            sampling_frequency=sampling_frequency,
                            use_first_half=self.use_first_half
                        )
                    )

                    if self.n_samples > n_injections_possible:
                        Logger.warning(
                            f"n_samples ({self.n_samples}) > injections possible ({n_injections_possible}), "
                            f"will only generate {n_injections_possible} samples per file"
                        )

                    time_wf_resampled, waveform_resampled = resample_waveform(
                        time_wf,
                        waveform_rescaled,
                        sampling_frequency
                    )

                    if waveform_resampled is None:
                        Logger.error(f"Failed to resample waveform for file {file_index}, skipping")
                        continue

                    Logger.info("Injecting waveforms into noise", verbose=False)
                    strain_with_injections, injection_log = WaveformInjector.inject_waveforms(
                        strain_noise=strain,
                        waveform=waveform_resampled,
                        injection_interval_seconds=self.injection_interval_seconds,
                        sampling_frequency=sampling_frequency,
                        sample_duration_seconds=sample_duration_seconds,
                        n_injections=self.n_samples + 2,
                        use_first_half=self.use_first_half
                    )

                    Logger.info("Applying whitening", verbose=False)
                    whitened_strain, _, _, _ = whitening(
                        strain_with_injections,
                        self.whitening_cut,
                        self.whitening_window,
                        sample_duration_seconds
                    )

                    Logger.info("Applying band-pass filter", verbose=False)
                    filtered_strain, _ = bandpass(
                        whitened_strain,
                        self.bandpass_fmin,
                        self.bandpass_fmax,
                        sample_duration_seconds
                    )

                    Logger.info("Creating windowed samples", verbose=False)
                    file_samples = self._create_windows(
                        filtered_strain,
                        sample_duration_seconds,
                        gps_start,
                        file_index,
                        detector,
                        distance,
                        injection_log
                    )
                    detector_samples.extend(file_samples)

                detector_samples = detector_samples[:self.n_samples]
                all_samples_by_distance[distance].extend(detector_samples)

        for distance in self.distances:
            Logger.info(f"Generated {len(all_samples_by_distance[distance])} samples at {distance} kpc")

        return all_samples_by_distance

    def _create_windows(
        self,
        s,
        delta_t: float,
        gps_start: float,
        file_index: int,
        detector: str,
        distance: float,
        injection_log: List[Dict]
    ) -> List[InjectionWindowedSample]:

        time_strain_cut = s.sample_times
        sample_points = int(self.window_size / delta_t)

        Twin_ini = []
        filtered_log = []

        for log_entry in injection_log:
            twin_start = log_entry["time_inj"] + 0.5 * (log_entry["waveform_duration"] - self.window_size)

            if twin_start >= time_strain_cut[0]:
                Twin_ini.append(twin_start)
                filtered_log.append(log_entry)

        locate_win = []
        for twin_start in Twin_ini:
            index = int(twin_start / delta_t) - int(time_strain_cut[0] / delta_t)
            locate_win.append(index)

        samples = []
        for j in range(len(filtered_log)):
            start = locate_win[j]
            end = start + sample_points

            if end > len(s):
                Logger.warning(f"Window {j} exceeds strain length, skipping", verbose=False)
                continue

            sample: InjectionWindowedSample = {
                "time": np.array(time_strain_cut[start:end]),
                "strain": np.array(s[start:end]),
                "sample_index": j,
                "file_index": file_index,
                "detector": detector,
                "gps_start": gps_start,
                "distance": distance,
                "snr": filtered_log[j]["snr"],
                "injection_time": filtered_log[j]["time_inj"]
            }
            samples.append(sample)

        return samples
