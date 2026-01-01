from jsonargparse import auto_cli
from pipeline import Pipeline
from core.utils.logger import Logger

def main(
    pipeline: Pipeline,
    destination: str,
    verbose: bool = False
):
    Logger.set_verbose(verbose)
    pipeline.execute(destination)

if __name__ == "__main__":
    auto_cli(main)
