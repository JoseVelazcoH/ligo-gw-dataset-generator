import os
import h5py
import numpy as np
from dataclasses import dataclass
from typing import Dict, Any

from core.strategies.base.exporter import ExporterBase
from core.types import InjectionTransformerData
from core.utils.logger import Logger

@dataclass
class H5InjectionExporter(ExporterBase):
    compression:str = "gzip"
    compression_opts: int = 4
    file_name_template: str= "gw_strain_{distance}_kpc"

    def export(self, data: InjectionTransformerData, destination: str, **kwargs) -> None:
        os.makedirs(destination, exist_ok=True)

        for distance, samples in data.items():
            if not samples:
                Logger.warning(f"No samples for distance {distance} kpc, skipping")
                continue

            Logger.info(f"Exporting {len(samples)} samples at {distance} kpc to HDF5.")

            file_name = self.file_name_template.format(distance=distance)
            output_file = os.path.join(destination, f"{file_name}.h5")

            times = np.stack([s['time'] for s in samples])
            strains = np.stack([s['strain'] for s in samples])
            sample_indices = np.array([s['sample_index'] for s in samples], dtype=np.int32)
            file_indices = np.array([s['file_index'] for s in samples], dtype=np.int32)
            detectors = np.array([s['detector'] for s in samples], dtype='S10')
            gps_starts = np.array([s['gps_start'] for s in samples], dtype=np.float64)
            distances_array = np.array([s['distance'] for s in samples], dtype=np.float64)
            snrs = np.array([s['snr'] for s in samples], dtype=np.float64)
            injection_times = np.array([s['injection_time'] for s in samples], dtype=np.float64)

            with h5py.File(output_file, 'w') as f:
                f.create_dataset(
                    'times',
                    data=times,
                    compression=self.compression,
                    compression_opts=self.compression_opts
                )
                f.create_dataset(
                    'strains',
                    data=strains,
                    compression=self.compression,
                    compression_opts=self.compression_opts
                )
                f.create_dataset(
                    'sample_indices',
                    data=sample_indices,
                    compression=self.compression,
                    compression_opts=self.compression_opts
                )
                f.create_dataset(
                    'file_indices',
                    data=file_indices,
                    compression=self.compression,
                    compression_opts=self.compression_opts
                )
                f.create_dataset(
                    'detectors',
                    data=detectors
                )
                f.create_dataset(
                    'gps_starts',
                    data=gps_starts,
                    compression=self.compression,
                    compression_opts=self.compression_opts
                )
                f.create_dataset(
                    'distances',
                    data=distances_array,
                    compression=self.compression,
                    compression_opts=self.compression_opts
                )
                f.create_dataset(
                    'snrs',
                    data=snrs,
                    compression=self.compression,
                    compression_opts=self.compression_opts
                )
                f.create_dataset(
                    'injection_times',
                    data=injection_times,
                    compression=self.compression,
                    compression_opts=self.compression_opts
                )

                metadata = self._extract_metadata(samples, distance)
                for key, value in metadata.items():
                    f.attrs[key] = value

            Logger.info(f"Dataset saved to: {output_file}")
            Logger.info(f"Shape: {strains.shape}", verbose=False)
            Logger.info(f"Size: {os.path.getsize(output_file) / 1024 / 1024:.2f} MB", verbose=False)

    def _extract_metadata(self, samples: list, distance: float) -> Dict[str, Any]:
        if not samples:
            return {}

        first_sample = samples[0]
        window_duration = first_sample['time'][-1] - first_sample['time'][0]
        sampling_rate = len(first_sample['time']) / window_duration

        unique_detectors = sorted(set(s['detector'] for s in samples))
        unique_gps_starts = sorted(set(s['gps_start'] for s in samples))

        snr_values = [s['snr'] for s in samples]

        return {
            'n_samples': len(samples),
            'distance_kpc': distance,
            'window_duration': window_duration,
            'sampling_rate': sampling_rate,
            'n_points_per_sample': len(first_sample['time']),
            'detectors': ','.join(unique_detectors),
            'n_files': len(set(s['file_index'] for s in samples)),
            'gps_start_min': min(unique_gps_starts),
            'gps_start_max': max(unique_gps_starts),
            'snr_min': min(snr_values),
            'snr_max': max(snr_values),
            'snr_mean': np.mean(snr_values),
            'snr_std': np.std(snr_values)
        }
