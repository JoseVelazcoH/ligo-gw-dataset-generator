from jsonargparse import auto_cli
from pipeline import Pipeline

def main(
    pipeline: Pipeline,
    source: str,
    destination: str
):
    pipeline.execute(source, destination)

if __name__ == "__main__":
    auto_cli(main)
