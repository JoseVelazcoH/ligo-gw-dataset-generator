import time
from dataclasses import dataclass

from core.strategies.base.loader import LoaderBase
from core.strategies.base.transformer import TransformerBase
from core.strategies.base.exporter import ExporterBase
from core.utils.logger import Logger

@dataclass
class Pipeline:
    loader: LoaderBase
    transformer: TransformerBase
    exporter: ExporterBase

    def execute(self, destination: str):
        start_time = time.time()
        Logger.info("Starting Pipeline Execution", verbose=False)
        data = self.loader.load()
        processed_data = self.transformer.transform(data)
        self.exporter.export(processed_data, destination)
        Logger.info("Pipeline Execution Completed.")
        end_time = time.time()
        Logger.info(f"Execution time: {round(end_time - start_time, 2)}", verbose=False)
        return processed_data
