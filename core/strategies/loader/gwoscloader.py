import fsspec
import h5py
import tempfile
import os
from dataclasses import dataclass
from typing import Dict, List

from core.strategies.base.loader import LoaderBase
from core.handlers.gwosc_data_fetcher import GWOSCDataFetcher
from core.utils.logger import Logger
from core.types.custom_types import LoaderData

@dataclass
class GWOSCLoader(LoaderBase):
    detectors: List[str] = None
    n_samples: List[str] = 1

    def load(self, **kwargs) -> LoaderData:
        urls = GWOSCDataFetcher.match_gwosc_strain_timelines(
            n_samples=self.n_samples
        )

        data = dict()
        for detector in self.detectors:
            data[detector] = dict()
            for index in range(len(urls[detector])):
                detector_data = self._files_from_url(urls[detector][index])
                data[detector][index] = detector_data
                Logger.info(f"Loaded data for {detector}, file {index + 1}")

        return data

    def _files_from_url(self, url: str) -> Dict:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_file = os.path.join(temp_dir, "temp_data.hdf5")

            Logger.info(f"Downloading file from URL: {url}", verbose=False)
            with fsspec.open(url, mode="rb") as remote_f:
                with open(temp_file, "wb") as local_f:
                    local_f.write(remote_f.read())

            Logger.info(f"Reading temp file: {temp_file}", verbose=False)
            with h5py.File(temp_file, "r") as file:
                strain = file['strain']['Strain'][()]
                delta_t = file['strain']['Strain'].attrs['Xspacing']
                time_sampling = file['strain']['Strain'].attrs['Xspacing']
                meta = file['meta']
                gps_start = meta['GPSstart'][()]
                duration = meta['Duration'][()]

        return {
            "strain": strain,
            "gps_start": gps_start,
            "duration": duration,
            "time_sampling": time_sampling,
            "delta_t": delta_t
        }
