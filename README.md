# LIGO GW Dataset Generator

A flexible and extensible pipeline for generating gravitational wave datasets from LIGO data. This tool downloads, processes, and exports gravitational wave strain data in a format suitable for machine learning applications.

## Features

- **Strategy Pattern Architecture**: The pipeline uses the Strategy pattern, allowing you to swap different implementations of loaders, transformers, and exporters without modifying the core pipeline logic
- **Configuration-Based Design**: Complete pipeline configuration through YAML files, enabling easy experimentation with different processing strategies
- **Dependency Injection**: Components are injected through configuration, promoting loose coupling and high testability
- **Extensibility**: Add new data sources, processing methods, or export formats by implementing the base strategy interfaces
- **Pipeline Pattern**: Three-stage data flow (Load → Transform → Export) that ensures clear separation of concerns
- **CLI Interface**: Simple command-line interface with configuration override capabilities

## Architecture

The pipeline follows a three-stage architecture where each stage can have multiple strategy implementations:

```
┌─────────┐      ┌─────────────┐      ┌──────────┐
│ Loader  │ ───> │ Transformer │ ───> │ Exporter │
└─────────┘      └─────────────┘      └──────────┘
```

### Components

1. **Loader**: Fetches raw data from sources
2. **Transformer**: Processes and transforms the raw data
3. **Exporter**: Exports processed data to various formats

Each component implements a base strategy interface, allowing you to create custom implementations for different data sources, processing techniques, or output formats.

### Default Strategies

The default configuration uses:
- **GWOSCLoader**: Downloads gravitational wave data from GWOSC
- **NoiseTransformer**: Applies whitening, band-pass filtering, and creates windowed samples
- **H5NoiseExporter**: Exports to HDF5 format with compression

You can replace any of these with your own implementations by creating new strategy classes and updating the configuration file.

## Installation

### Setup

1. Clone the repository

```bash
git clone https://github.com/JoseVelazcoH/ligo-gw-dataset-generator.git
``` 
2. Create a virtual environment Install dependencies:

```bash
python -m venv .venv
pip install -r requirements.txt
```

## Usage

### Basic Usage

Run the pipeline with the default configuration:

```bash
python cli.py --config configs/default.yaml
```

### Configuration

The pipeline is configured through YAML files. The configuration specifies which strategy implementations to use for each stage and their initialization parameters.

Example configuration structure:

```yaml
pipeline:
  loader:
    class_path: core.strategies.loader.gwoscloader.GWOSCLoader
    init_args:
      detectors: [H1]
      n_samples: 10

  transformer:
    class_path: core.strategies.transformer.noise_transformer.NoiseTransformer
    init_args:
      detector: H1
      window_size: 2.0
      n_samples: 10

  exporter:
    class_path: core.strategies.exporter.h5_noise_exporter.H5NoiseExporter
    init_args:
      compression: gzip

destination: "output/h5_noise"
```

### Command-line Arguments

You can override configuration parameters directly from the command line:

```bash
python cli.py --config configs/default.yaml --destination output/custom_output
```
