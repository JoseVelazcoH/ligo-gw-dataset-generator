from core.strategies.loader import LoaderBase
from core.strategies.transformer import TransformerBase
from core.strategies.exporter import ExporterBase
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

    def execute(self, source: str, destination: str):
        Logger.info("Starting Pipeline Execution...")
        data = self.loader.load(source)
        processed_data = self.transformer.transform(data)
        self.exporter.export(processed_data, destination)
        Logger.info("Pipeline Execution Completed.")
        return processed_data
