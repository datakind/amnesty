#!/bin/sh

# First, run the python script to extract the lotus db:

echo "Processing lotus db into CSV..."
python parse_lotus_database.py

echo "Adding country labels..."
Rscript iso3-encoding.R

echo "Breaking out categories..."
python add_category_labels.py