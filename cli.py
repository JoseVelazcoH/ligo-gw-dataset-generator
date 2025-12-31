from jsonargparse import auto_cli
from pipeline import Pipeline

def main(
    pipeline: Pipeline,
    destination: str
):
    pipeline.execute(destination)

if __name__ == "__main__":
    auto_cli(main)
