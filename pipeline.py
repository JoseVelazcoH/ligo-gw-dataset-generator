from core.strategies.base.loader import LoaderBase
from core.strategies.base.transformer import TransformerBase
from core.strategies.base.exporter import ExporterBase
from core.utils.logger import Logger

class Pipeline:
    def __init__(
        self,
        loader: LoaderBase,
        transformer: TransformerBase,
        exporter: ExporterBase
    ):
        self.loader = loader
        self.transformer = transformer
        self.exporter = exporter

    def execute(self, destination: str):
        Logger.info("Starting Pipeline Execution...")
        data = self.loader.load()
        processed_data = self.transformer.transform(data)
        self.exporter.export(processed_data, destination)
        Logger.info("Pipeline Execution Completed.")
        return processed_data
