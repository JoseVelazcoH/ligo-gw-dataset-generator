from typing import List
import numpy as np
from dataclasses import dataclass

from core.strategies.base.transformer import TransformerBase
from core.types import LoaderData, TransformerData, WindowedSample
from core.utils.logger import Logger
from core.utils.preprocessing import whitening, bandpass

@dataclass
class NoiseTransformer(TransformerBase):
    detectors: List[str] =  None
    window_size: float = 2.0
    whitening_cut: int = 10
    whitening_window: float = 0.5
    bandpass_fmin: float = 100.0
    bandpass_fmax: float = 1600
    n_samples: int = 1
    use_second_half: bool = True

    def transform(self, data: LoaderData, **kwargs) -> TransformerData:
        all_samples = []

        for detector in self.detectors:
            if detector not in data:
                Logger.warning(f"Detector {detector} not found in loaded data, skipping")
                continue

            Logger.info(f"Processing noise data for detector {detector}")
            detector_files = data[detector]
            detector_samples = []

            for file_index, file_data in detector_files.items():
                if len(detector_samples) >= self.n_samples:
                    break

                Logger.info(f"Processing file {file_index + 1}/{len(detector_files)}", verbose=False)
                strain = file_data["strain"]
                ts = file_data["time_sampling"]
                gps_start = file_data["gps_start"]

                strain_copy = np.copy(strain)

                Logger.info("Starting whitening process", verbose=False)
                whitened_strain, _, _, _ = whitening(
                    strain_copy,
                    self.whitening_cut,
                    self.whitening_window,
                    ts
                )

                Logger.info("Applying band-pass filter", verbose=False)
                filtered_strain, _ = bandpass(
                    whitened_strain,
                    self.bandpass_fmin,
                    self.bandpass_fmax,
                    ts
                )

                Logger.info("Creating windowed samples", verbose=False)
                file_samples = self._create_windows(
                    filtered_strain,
                    ts,
                    gps_start,
                    file_index,
                    detector
                )
                detector_samples.extend(file_samples)

            detector_samples = detector_samples[:self.n_samples]
            all_samples.extend(detector_samples)

        Logger.info(f"Generated {len(all_samples)} total windowed samples")
        return all_samples

    def _create_windows(
        self,
        strain,
        delta_t: float,
        gps_start: float,
        file_index: int,
        detector: str
    ) -> List[WindowedSample]:
        time_strain = strain.sample_times
        sample_points = int(self.window_size / delta_t)

        total_samples = len(strain)

        if self.use_second_half:
            Logger.warning("Using only second half of strain for noise samples")
            half_samples = total_samples // 2
            start_index_offset = half_samples
            available_samples = total_samples - half_samples
        else:
            Logger.warning("Using entire strain for noise samples")
            start_index_offset = 0
            available_samples = total_samples

        available_duration = available_samples * delta_t
        n_possible_samples = int(available_duration / self.window_size)

        if n_possible_samples == 0:
            Logger.warning("Insufficient data for even one window sample")
            return []

        samples = []
        for i in range(n_possible_samples):
            start_index = start_index_offset + i * sample_points
            end_index = start_index + sample_points

            if end_index > len(strain):
                Logger.warning(f"Window {i} exceeds strain length, stopping", verbose=False)
                break

            sample: WindowedSample = {
                "time": np.array(time_strain[start_index:end_index]),
                "strain": np.array(strain[start_index:end_index]),
                "sample_index": i,
                "file_index": file_index,
                "detector": detector,
                "gps_start": gps_start
            }
            samples.append(sample)

        return samples
