# Evaluation Benchmarks

This repository contains a few helper files that allow us to communicate with a proving an verifiaction service task worker and the experiment and evaluation notebooks to produce the statistics in the paper.

## Getting Started

Simply install this repositories code through pip:

```
pip install -r requirements.txt
```

## Experiment reproduction

The experimetns PCF activities are configured in [experiments.json](experiments.json)

### Execute the Debug non-proving processes to gain baseline data

1. Start a service task worker in proving Debug mode running on ```localhost:50051```

2. Run the [debug_experiments.ipynb](debug_experiments.ipynb) notebook in a Jupyter Server

### Collect the 'real' proving processes to gain the actual experiment data


1. Start a service task worker in normal proving mode running on ```localhost:50051```

2. Run the [generated_experiments.ipynb](generated_experiments.ipynb) notebook in a Jupyter Server

## Evaluation Reproduction

The evaluation can easily be reexecuted by executing the [evaluation.ipynb](evaluation.ipynb) and more importantly the [evaluation_generated.ipynb](evaluation_generated.ipynb).
They require that the previous Experiment notebooks complete successfully and save the resulting figures as pdfs and eps files in this folder. 


