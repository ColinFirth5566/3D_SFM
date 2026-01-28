#!/bin/bash

# Installation script for 3D Gaussian Splatting with COLMAP
# Run this script to install all required dependencies

echo "=== Installing COLMAP ==="
sudo apt-get update
sudo apt-get install -y colmap

echo ""
echo "=== Verifying COLMAP installation ==="
colmap -h | head -5

echo ""
echo "=== Installation complete! ==="
echo "COLMAP installed successfully"
