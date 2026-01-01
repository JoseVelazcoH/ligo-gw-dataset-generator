from typing import List
import numpy as np
from core.strategies.base.transformer import TransformerBase
from core.types import LoaderData, TransformerData, WindowedSample
from core.utils.logger import Logger
from core.utils.preprocessing import Preprocessing

class NoiseTransformer(TransformerBase):
    def __init__(
        self,
        detectors: List[str] = None,
        window_size: float = 2.0,
        whitening_cut: int = 10,
        whitening_window: float = 0.5,
        bandpass_fmin: float = 100.0,
        bandpass_fmax: float = 1600.0,
        n_samples: int = 1
    ):
        self.detectors = detectors or ["H1", "L1", "V1"]
        self.window_size = window_size
        self.whitening_cut = whitening_cut
        self.whitening_window = whitening_window
        self.bandpass_fmin = bandpass_fmin
        self.bandpass_fmax = bandpass_fmax
        self.n_samples = n_samples

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
                if file_index >= self.n_samples:
                    break

                Logger.info(f"Processing file {file_index + 1}/{len(detector_files)}", verbose=False)
                strain = file_data["strain"]
                ts = file_data["time_sampling"]
                gps_start = file_data["gps_start"]

                strain_copy = np.copy(strain)

                Logger.info("Starting whitening process", verbose=False)
                whitened_strain, _, _, _ = Preprocessing.whitening(
                    strain_copy,
                    self.whitening_cut,
                    self.whitening_window,
                    ts
                )

                Logger.info("Applying band-pass filter", verbose=False)
                filtered_strain, _ = Preprocessing.bandpass(
                    whitened_strain,
                    self.bandpass_fmin,
                    self.bandpass_fmax,
                    ts
                )

                Logger.info("Creating windowed samples", verbose=False)
                file_samples = self._create_windows(filtered_strain, ts, gps_start, file_index, detector)
                detector_samples.extend(file_samples)

            detector_samples = detector_samples[:self.n_samples]
            all_samples.extend(detector_samples)

        Logger.info(f"Generated {len(all_samples)} total windowed samples")
        return all_samples

    def _create_windows(
        self,
        s,
        delta_t: float,
        gps_start: float,
        file_index: int,
        detector: str
    ) -> List[WindowedSample]:
        time_strain_cut = s.sample_times
        sample_points = int(self.window_size / delta_t)

        start_offset = 4096 * int(4096 / 2)
        available_time = 4090 - time_strain_cut[start_offset]
        n_samples = int(available_time / self.window_size)

        samples = []
        for i in range(n_samples):
            start = i * sample_points + start_offset
            end = start + sample_points

            sample: WindowedSample = {
                "time": np.array(time_strain_cut[start:end]),
                "strain": np.array(s[start:end]),
                "sample_index": i,
                "file_index": file_index,
                "detector": detector,
                "gps_start": gps_start
            }
            samples.append(sample)

        return samples
