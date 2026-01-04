import h5py
import numpy as np
from typing import Dict, Any
from dataclasses import dataclass

from core.strategies.base.loader import LoaderBase
from core.utils.logger import Logger

@dataclass
class WaveformLoader(LoaderBase):
    waveform_path: str

    def load(self, **kwargs) -> Dict[str, Any]:
        Logger.info(f"Loading waveform from {self.waveform_path}")

        with h5py.File(self.waveform_path, 'r') as f:
            group_key = list(f.keys())[0]
            waveform_data = np.array(f[group_key])

            time = waveform_data[:, 0]
            h_plus = waveform_data[:, 1]
            h_cross = waveform_data[:, 2]

        Logger.info(f"Waveform loaded: {len(time)} points, duration: {time[-1] - time[0]:.4f}s")

        return {
            "time": time,
            "h_plus": h_plus,
            "h_cross": h_cross
        }
