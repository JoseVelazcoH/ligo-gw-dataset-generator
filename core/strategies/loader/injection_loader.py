from typing import List

from core.strategies.base.loader import LoaderBase
from core.strategies.loader.gwoscloader import GWOSCLoader
from core.strategies.loader.waveform_loader import WaveformLoader
from core.types import InjectionLoaderData
from core.utils.logger import Logger


class InjectionLoader(LoaderBase):
    def __init__(
        self,
        waveform_path: str,
        detectors: List[str] = None,
        n_samples: int = 1
    ):
        self.gwosc_loader = GWOSCLoader(
            detectors=detectors,
            n_samples=n_samples
        )
        self.waveform_loader = WaveformLoader(
            waveform_path=waveform_path
        )

    def load(self, **kwargs) -> InjectionLoaderData:
        Logger.info("Loading strain data from GWOSC")
        strain_data = self.gwosc_loader.load(**kwargs)

        Logger.info("Loading waveform data")
        waveform_data = self.waveform_loader.load(**kwargs)

        return {
            "strain": strain_data,
            "waveform": waveform_data
        }
