#!/bin/bash

# Directories
RAW_DIR="raw"
TRAIN_DIR="train"
TEST_DIR="test"

# Create train and test directories if they do not exist
mkdir -p "$TRAIN_DIR"
mkdir -p "$TEST_DIR"

# Total number of jpg files in the raw directory
TOTAL_FILES=$(ls "$RAW_DIR"/*.jpg | wc -l)

# Calculate the number of files to move to train and test
TRAIN_COUNT=$((TOTAL_FILES * 80 / 100))
TEST_COUNT=$((TOTAL_FILES - TRAIN_COUNT))

# Shuffle and split the files
shuf -n "$TRAIN_COUNT" -e "$RAW_DIR"/*.jpg | xargs -I{} mv {} "$TRAIN_DIR"
shuf -n "$TEST_COUNT" -e "$RAW_DIR"/*.jpg | xargs -I{} mv {} "$TEST_DIR"

echo "Moved $TRAIN_COUNT files to $TRAIN_DIR"
echo "Moved $TEST_COUNT files to $TEST_DIR"
