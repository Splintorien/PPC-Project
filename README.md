# PPC-Project: Energy market simulation

This project was made as the final project of the PPC module at INSA Lyon. It was made by Bryan Djafer and Mathis Chapuis.

## Installation guide

To manage your dependencies, you might want to use **virtualenv** or **miniconda**.

In order to install the Python dependencies, run the following command:

```bash
pip install -r requirements.txt
```

## Run the market market simulation

This simulation can be either run in a Docker container or manually. To run the simulation with Docker, run the following command to build the container:

```bash
docker build --tag ppc-simulation .
```

Then to lauch the simulation, run:

```bash
docker run -it --rm -v $PWD:/ppc --name container-ppc-simulation ppc-simulation
```

I you don't want to use Docker, you can still lauch the project by using:

```bash
python simulation.py <config file>
```

You have a config template file named `config.json` that you can modify to change the simulation parameters.

## Linting and formating

In order to run the linting for the project, run the following command:

```bash
pylint market_simulation
```

In order to format the code before committing or pushing, run the following command:

```bash
black market_simulation
```
