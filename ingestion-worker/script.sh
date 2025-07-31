#!/bin/bash

source $(conda info --base)/etc/profile.d/conda.sh
conda activate news


TOPICS=$(cat topics.txt | tr '\n' ' ')
# Run the pipeline
python3 run_pipeline.py --mode batch --topics $TOPICS

