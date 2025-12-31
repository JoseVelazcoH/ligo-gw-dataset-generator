import os
import h5py
import numpy as np
from typing import Dict, Any
from core.strategies.base.exporter import ExporterBase
from core.types import TransformerData
from core.utils.logger import Logger

class H5NoiseExporter(ExporterBase):
    def __init__(
        self,
        # base_dir: str = "output",
        compression: str = "gzip",
        compression_opts: int = 4,
        file_name: str = "noise_dataset"
    ):
        # self.base_dir = base_dir
        self.compression = compression
        self.compression_opts = compression_opts
        self.file_name = file_name

    def export(self, data: TransformerData, destination: str, **kwargs) -> None:
        Logger.info(f"Exporting {len(data)} samples to HDF5...")

        os.makedirs(destination, exist_ok=True)

        # output_file = os.path.join(self.base_dir, f"{destination}.h5")
        output_file = os.path.join(destination, f"{self.file_name}.h5")


        times = np.stack([s['time'] for s in data])
        strains = np.stack([s['strain'] for s in data])
        sample_indices = np.array([s['sample_index'] for s in data], dtype=np.int32)
        file_indices = np.array([s['file_index'] for s in data], dtype=np.int32)
        detectors = np.array([s['detector'] for s in data], dtype='S10')
        gps_starts = np.array([s['gps_start'] for s in data], dtype=np.float64)

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

            metadata = self._extract_metadata(data)
            for key, value in metadata.items():
                f.attrs[key] = value

        Logger.info(f"Dataset saved to: {output_file}")
        Logger.info(f"Shape: {strains.shape}")
        Logger.info(f"Size: {os.path.getsize(output_file) / 1024 / 1024:.2f} MB")

    def _extract_metadata(self, data: TransformerData) -> Dict[str, Any]:
        if not data:
            return {}

        first_sample = data[0]
        window_duration = first_sample['time'][-1] - first_sample['time'][0]
        sampling_rate = len(first_sample['time']) / window_duration

        unique_detectors = sorted(set(s['detector'] for s in data))
        unique_gps_starts = sorted(set(s['gps_start'] for s in data))

        return {
            'n_samples': len(data),
            'window_duration': window_duration,
            'sampling_rate': sampling_rate,
            'n_points_per_sample': len(first_sample['time']),
            'detectors': ','.join(unique_detectors),
            'n_files': len(set(s['file_index'] for s in data)),
            'gps_start_min': min(unique_gps_starts),
            'gps_start_max': max(unique_gps_starts),
        }
