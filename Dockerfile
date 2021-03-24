FROM python:3.8-slim

WORKDIR /ppc

COPY . .

RUN apt-get update \
    && apt-get upgrade gcc -y \
    && pip install --upgrade pip \
    && pip install -r requirements.txt \
    && rm requirements.txt

CMD ["python", "market_simulation/simulation.py", "market_simulation/config.json"]
