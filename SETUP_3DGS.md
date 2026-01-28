# Complete Setup Guide for Real 3D Gaussian Splatting

Your system is ready! You have:
- ✅ NVIDIA GeForce RTX 3060 Laptop GPU (6GB VRAM)
- ✅ CUDA 13.0 Driver Support
- ✅ PyTorch 2.5.1 with CUDA 12.1 installed
- ✅ Ubuntu 24.04 in WSL2

## What You Need to Install

### Step 1: Install COLMAP (requires sudo)

```bash
cd /mnt/c/Code/3D_SFM
./INSTALL_COMMANDS.sh
```

Or manually:
```bash
sudo apt-get update
sudo apt-get install -y colmap
colmap -h  # Verify installation
```

### Step 2: Install CUDA Toolkit (for compiling 3DGS)

```bash
# Install CUDA 12.1 toolkit
wget https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2404/x86_64/cuda-keyring_1.1-1_all.deb
sudo dpkg -i cuda-keyring_1.1-1_all.deb
sudo apt-get update
sudo apt-get install -y cuda-toolkit-12-1

# Add to ~/.bashrc
echo 'export PATH=/usr/local/cuda-12.1/bin:$PATH' >> ~/.bashrc
echo 'export LD_LIBRARY_PATH=/usr/local/cuda-12.1/lib64:$LD_LIBRARY_PATH' >> ~/.bashrc
echo 'export CUDA_HOME=/usr/local/cuda-12.1' >> ~/.bashrc
source ~/.bashrc
```

### Step 3: Install 3D Gaussian Splatting

```bash
cd /mnt/c/Code/3D_SFM/backend
source venv/bin/activate

# Navigate to the cloned 3DGS repo
cd /tmp/gaussian-splatting

# Install the submodules
pip install submodules/diff-gaussian-rasterization
pip install submodules/simple-knn
```

### Step 4: Move 3DGS to permanent location

```bash
sudo mkdir -p /opt/gaussian-splatting
sudo chown $USER:$USER /opt/gaussian-splatting
cp -r /tmp/gaussian-splatting/* /opt/gaussian-splatting/
```

### Step 5: Update Backend Configuration

```bash
cd /mnt/c/Code/3D_SFM/backend
cat > .env << 'EOF'
COLMAP_BIN=colmap
GS_IMPLEMENTATION=original
GAUSSIAN_SPLATTING_PATH=/opt/gaussian-splatting
HOST=0.0.0.0
PORT=8000
EOF
```

### Step 6: Restart Backend

```bash
cd /mnt/c/Code/3D_SFM/backend
source venv/bin/activate
python main.py
```

## Alternative: Quick Test Without Installing Everything

If you want to test the reconstruction pipeline works before installing CUDA toolkit:

I can create a test script that uses PyTorch's built-in CUDA without needing the full toolkit.

## Verification Steps

After installation, verify:

```bash
# Check COLMAP
colmap -h

# Check CUDA
nvcc --version

# Check PyTorch CUDA
python -c "import torch; print(torch.cuda.is_available())"

# Check 3DGS installation
cd /opt/gaussian-splatting
ls -la submodules/
```

## Memory Considerations

Your RTX 3060 Laptop has 6GB VRAM. For best results:
- Use 10-15 images (not 20)
- Keep images at 720p or lower
- Reduce training iterations to 3000-5000

## Next Steps

After installation:
1. Run the backend with real 3DGS
2. Upload your face photos
3. Wait 10-30 minutes for reconstruction
4. View the real 3D model!

## Troubleshooting

**CUDA out of memory:**
- Reduce image resolution
- Use fewer images (10 instead of 20)
- Edit `backend/reconstruction.py` line 223: change `--iterations 7000` to `--iterations 3000`

**COLMAP fails:**
- Make sure images have good overlap (70%+)
- Check images are not blurry
- Try with fewer images first

**3DGS compilation fails:**
- Make sure CUDA_HOME is set: `echo $CUDA_HOME`
- Verify nvcc works: `nvcc --version`
- Check PyTorch CUDA: `python -c "import torch; print(torch.cuda.is_available())"`
