import subprocess
import sys
import os
import struct
from pathlib import Path
from typing import AsyncGenerator, Tuple
import asyncio
import json
import shutil
import numpy as np
from plyfile import PlyData, PlyElement
from PIL import Image


class GaussianSplattingPipeline:
    """
    Handles the 3D reconstruction pipeline using 3D Gaussian Splatting (3DGS)

    Pipeline stages:
    1. COLMAP - Structure from Motion for camera poses
    2. 3DGS Training - Train gaussian splat representation
    3. Export - Convert to web-friendly format (PLY/GLTF)
    """

    def __init__(self, job_id: str, upload_dir: Path, output_dir: Path, fast_mode: bool = True):
        self.job_id = job_id
        self.input_dir = upload_dir / job_id
        self.output_dir = output_dir / job_id
        self.output_dir.mkdir(exist_ok=True)
        self.fast_mode = fast_mode  # Fast mode for <5 min processing

        # Binary paths - configure via environment variables
        self.colmap_bin = os.getenv("COLMAP_BIN", "colmap")
        self.gaussian_splatting_path = os.getenv("GAUSSIAN_SPLATTING_PATH", "/opt/gaussian-splatting")

        # Fast mode settings — target <5 min total for 12 images with MVS
        if self.fast_mode:
            self.max_image_size = 1000  # Good quality, fast PatchMatchStereo
            self.gs_iterations = 5000  # Dense MVS init converges faster
            self.sift_max_features = 8192  # Full features for better matching
        else:
            self.max_image_size = 1920  # Full HD
            self.gs_iterations = 7000  # Full quality
            self.sift_max_features = 8192

        # Working directories
        self.colmap_dir = self.output_dir / "colmap"
        self.sparse_dir = self.colmap_dir / "sparse" / "0"
        self.distorted_dir = self.colmap_dir / "distorted"
        self.gs_output_dir = self.output_dir / "gaussian_splatting"

        for dir in [self.colmap_dir, self.sparse_dir, self.distorted_dir, self.gs_output_dir]:
            dir.mkdir(exist_ok=True, parents=True)

        # Copy images to colmap input directory
        self.images_dir = self.colmap_dir / "input"
        self.images_dir.mkdir(exist_ok=True)

    async def run(self) -> AsyncGenerator[Tuple[int, str], None]:
        """
        Run the complete 3DGS reconstruction pipeline
        Yields progress updates as (progress_percentage, stage_description)
        """

        try:
            # Check if we're in simulation mode
            implementation = os.getenv("GS_IMPLEMENTATION", "auto")
            is_simulation = implementation == "simulation"

            # Step 1: Prepare images (0-5%)
            yield 2, "Preparing images..."
            await self._prepare_images()
            yield 5, "Images prepared"

            if not is_simulation:
                # Real COLMAP pipeline
                # Step 2: COLMAP feature extraction (5-15%)
                yield 8, "Extracting features with COLMAP..."
                await self._run_colmap_feature_extraction()
                yield 15, "Features extracted"

                # Step 3: COLMAP feature matching (15-25%)
                yield 18, "Matching features..."
                await self._run_colmap_matching()
                yield 25, "Features matched"

                # Step 4: COLMAP sparse reconstruction (25-35%)
                yield 28, "Computing camera poses (SfM)..."
                await self._run_colmap_mapper()
                yield 35, "Camera poses computed"

                # Step 5: COLMAP undistortion (35-38%)
                yield 36, "Undistorting images..."
                await self._run_colmap_undistortion()
                yield 38, "Images undistorted"

                # Step 6: MVS dense reconstruction (38-60%)
                yield 40, "Computing dense depth maps (PatchMatch MVS)..."
                await self._run_colmap_patch_match_stereo()
                yield 55, "Dense depth maps computed"

                yield 56, "Fusing dense point cloud..."
                fused_ply = await self._run_colmap_stereo_fusion()
                yield 60, "Dense point cloud fused"

                # Step 7: Prepare dense initialization for 3DGS (60-63%)
                yield 61, "Preparing dense initialization..."
                await self._convert_colmap_to_gs_format()
                num_dense = self._replace_sparse_with_dense(fused_ply, max_points=50000)
                yield 63, f"Dense initialization ready ({num_dense} points)"
            else:
                # Simulation: just report progress
                yield 10, "Simulating feature extraction..."
                await asyncio.sleep(0.5)
                yield 15, "Features extracted (simulated)"

                yield 18, "Simulating feature matching..."
                await asyncio.sleep(0.5)
                yield 25, "Features matched (simulated)"

                yield 28, "Simulating camera pose computation..."
                await asyncio.sleep(0.5)
                yield 35, "Camera poses computed (simulated)"

                yield 36, "Simulating image undistortion..."
                await asyncio.sleep(0.3)
                yield 38, "Images undistorted (simulated)"

                yield 40, "Simulating dense reconstruction..."
                await asyncio.sleep(1.0)
                yield 63, "Dense reconstruction simulated"

            # Step 8: 3D Gaussian Splatting training (63-95%)
            yield 65, "Training 3D Gaussian Splatting model..."
            async for progress in self._run_gaussian_splatting():
                # Map 0-100% of training to 63-95% overall
                overall_progress = 63 + int(progress * 0.32)
                yield overall_progress, f"Training gaussians... ({int(progress)}%)"
            yield 95, "Gaussian splatting complete"

            # Step 7: Export to web format (95-100%)
            yield 97, "Exporting model..."
            await self._export_model()
            yield 100, "Model ready"

        except Exception as e:
            raise Exception(f"3DGS reconstruction failed: {str(e)}")

    async def _run_command(self, command: list, error_msg: str, cwd: Path = None):
        """Run a subprocess command asynchronously"""
        process = await asyncio.create_subprocess_exec(
            *command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=str(cwd) if cwd else None
        )

        stdout, stderr = await process.communicate()

        if process.returncode != 0:
            error_output = stderr.decode() if stderr else stdout.decode()
            raise Exception(f"{error_msg}: {error_output}")

        return stdout.decode()

    async def _prepare_images(self):
        """Copy, resize, and prepare images for COLMAP"""
        images = sorted(self.input_dir.glob("*.*"))

        for img in images:
            if img.suffix.lower() in ['.jpg', '.jpeg', '.png']:
                dest = self.images_dir / img.name

                # Resize image for faster processing
                try:
                    with Image.open(img) as pil_img:
                        # Convert to RGB if necessary (handles RGBA, palette, etc.)
                        if pil_img.mode != 'RGB':
                            pil_img = pil_img.convert('RGB')

                        # Calculate new size maintaining aspect ratio
                        width, height = pil_img.size
                        max_dim = max(width, height)

                        if max_dim > self.max_image_size:
                            scale = self.max_image_size / max_dim
                            new_width = int(width * scale)
                            new_height = int(height * scale)
                            pil_img = pil_img.resize((new_width, new_height), Image.LANCZOS)

                        # Save as JPEG for faster processing (smaller files)
                        dest_jpg = self.images_dir / f"{img.stem}.jpg"
                        pil_img.save(dest_jpg, "JPEG", quality=90)
                except Exception as e:
                    # Fallback: just copy the file
                    shutil.copy2(img, dest)

    async def _run_colmap_feature_extraction(self):
        """Extract features using COLMAP with optimized settings"""
        database_path = self.colmap_dir / "database.db"

        command = [
            self.colmap_bin,
            "feature_extractor",
            "--database_path", str(database_path),
            "--image_path", str(self.images_dir),
            "--ImageReader.single_camera", "1",
            "--ImageReader.camera_model", "OPENCV",
            "--FeatureExtraction.use_gpu", "1" if self._check_gpu() else "0",
            "--SiftExtraction.max_num_features", str(self.sift_max_features),
        ]

        # Use all CPU cores for feature extraction
        command.extend([
            "--FeatureExtraction.num_threads", "-1",
        ])

        await self._run_command(command, "COLMAP feature extraction failed")

    async def _run_colmap_matching(self):
        """Match features using COLMAP with optimized settings"""
        database_path = self.colmap_dir / "database.db"

        # Always use exhaustive matcher — images may not be in capture order
        command = [
            self.colmap_bin,
            "exhaustive_matcher",
            "--database_path", str(database_path),
            "--FeatureMatching.use_gpu", "1" if self._check_gpu() else "0",
        ]

        await self._run_command(command, "COLMAP feature matching failed")

    async def _run_colmap_mapper(self):
        """Run COLMAP sparse reconstruction (Structure from Motion)"""
        database_path = self.colmap_dir / "database.db"

        command = [
            self.colmap_bin,
            "mapper",
            "--database_path", str(database_path),
            "--image_path", str(self.images_dir),
            "--output_path", str(self.colmap_dir / "sparse"),
        ]

        await self._run_command(command, "COLMAP mapper failed")

    async def _run_colmap_undistortion(self):
        """Undistort images for 3DGS training"""
        command = [
            self.colmap_bin,
            "image_undistorter",
            "--image_path", str(self.images_dir),
            "--input_path", str(self.sparse_dir),
            "--output_path", str(self.distorted_dir),
            "--output_type", "COLMAP",
        ]

        await self._run_command(command, "COLMAP undistortion failed")

    async def _run_colmap_patch_match_stereo(self):
        """Run COLMAP PatchMatchStereo to compute dense depth maps"""
        command = [
            self.colmap_bin,
            "patch_match_stereo",
            "--workspace_path", str(self.distorted_dir),
            "--workspace_format", "COLMAP",
            "--PatchMatchStereo.max_image_size", str(self.max_image_size),
            "--PatchMatchStereo.gpu_index", "0",
            "--PatchMatchStereo.geom_consistency", "true",
        ]

        if self.fast_mode:
            command.extend([
                "--PatchMatchStereo.window_radius", "5",  # Default 11, halved for speed
                "--PatchMatchStereo.num_iterations", "3",  # Default 5, reduced for speed
            ])

        await self._run_command(command, "COLMAP PatchMatchStereo failed")

    async def _run_colmap_stereo_fusion(self) -> Path:
        """Run COLMAP stereo fusion to create dense point cloud.
        Returns path to fused.ply.
        """
        fused_ply_path = self.distorted_dir / "fused.ply"

        command = [
            self.colmap_bin,
            "stereo_fusion",
            "--workspace_path", str(self.distorted_dir),
            "--workspace_format", "COLMAP",
            "--input_type", "geometric",
            "--output_path", str(fused_ply_path),
            "--StereoFusion.min_num_pixels", "3",
            "--StereoFusion.max_reproj_error", "2.0",
        ]

        await self._run_command(command, "COLMAP stereo fusion failed")

        if not fused_ply_path.exists():
            raise Exception("Stereo fusion completed but fused.ply not found")

        print(f"[MVS] Fused PLY: {fused_ply_path} ({fused_ply_path.stat().st_size} bytes)")
        return fused_ply_path

    async def _run_gaussian_splatting(self) -> AsyncGenerator[float, None]:
        """
        Run 3D Gaussian Splatting training

        Supports multiple implementations:
        1. Original 3DGS (graphdeco-inria/gaussian-splatting)
        2. Nerfstudio with splatfacto
        3. Custom implementation
        """

        # Check which implementation is available
        implementation = os.getenv("GS_IMPLEMENTATION", "auto")

        if implementation == "auto":
            # Auto-detect available implementation
            if self._check_gaussian_splatting_original():
                implementation = "original"
            elif self._check_nerfstudio():
                implementation = "nerfstudio"
            else:
                # Use simulation for testing
                implementation = "simulation"

        if implementation == "original":
            async for progress in self._run_gs_original():
                yield progress

        elif implementation == "nerfstudio":
            async for progress in self._run_nerfstudio():
                yield progress

        else:
            # Simulation mode for testing without GPU/3DGS installation
            async for progress in self._run_gs_simulation():
                yield progress

    async def _run_gs_original(self) -> AsyncGenerator[float, None]:
        """Run original 3DGS implementation with optimized settings"""
        print(f"[3DGS] Starting _run_gs_original")

        # Training command for original 3DGS
        train_script = Path(self.gaussian_splatting_path) / "train.py"
        print(f"[3DGS] train_script={train_script}, exists={train_script.exists()}")

        max_iterations = self.gs_iterations

        command = [
            sys.executable,
            str(train_script),
            "--source_path", str(self.distorted_dir),
            "--model_path", str(self.gs_output_dir),
            "--iterations", str(max_iterations),
            "--save_iterations", str(max_iterations),
            "--quiet",
            "--disable_viewer",
        ]

        # Densification settings (less aggressive with dense MVS initialization)
        command.extend([
            "--densify_until_iter", str(min(3500, max_iterations - 100)),
            "--densification_interval", "200",
        ])

        # Run training with progress monitoring
        print(f"[3DGS] Running command: {' '.join(command)}")
        process = await asyncio.create_subprocess_exec(
            *command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.STDOUT,
        )

        iteration = 0
        output_lines = []

        async for line in process.stdout:
            line_str = line.decode().strip()
            output_lines.append(line_str)

            # Parse iteration from training progress output
            if "Training progress" in line_str or "Iteration" in line_str:
                try:
                    # Parse percentage from tqdm-style output
                    if "%" in line_str:
                        pct_str = line_str.split("%")[0].split()[-1]
                        pct = float(pct_str)
                        yield pct
                    else:
                        parts = line_str.split()
                        for i, part in enumerate(parts):
                            if part == "Iteration":
                                iteration = int(parts[i + 1])
                                progress = (iteration / max_iterations) * 100
                                yield progress
                                break
                except:
                    pass

        await process.wait()
        print(f"[3DGS] Training process exited with code {process.returncode}")
        print(f"[3DGS] Last output lines: {output_lines[-5:] if output_lines else 'NONE'}")

        if process.returncode != 0:
            error_output = "\n".join(output_lines[-20:])
            raise Exception(f"3DGS training failed (exit code {process.returncode}): {error_output}")

        yield 100.0

    async def _run_nerfstudio(self) -> AsyncGenerator[float, None]:
        """Run Nerfstudio with splatfacto method"""

        # Convert COLMAP to Nerfstudio format
        ns_data_dir = self.output_dir / "nerfstudio_data"
        ns_data_dir.mkdir(exist_ok=True)

        # Process data
        command = [
            "ns-process-data",
            "images",
            "--data", str(self.images_dir),
            "--output-dir", str(ns_data_dir),
        ]

        await self._run_command(command, "Nerfstudio data processing failed")

        # Train with splatfacto using optimized iteration count
        command = [
            "ns-train",
            "splatfacto",
            "--data", str(ns_data_dir),
            "--output-dir", str(self.gs_output_dir),
            "--max-num-iterations", str(self.gs_iterations),
        ]

        # Monitor training progress
        process = await asyncio.create_subprocess_exec(
            *command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.STDOUT,
        )

        async for line in process.stdout:
            line_str = line.decode().strip()
            # Parse progress from Nerfstudio output
            if "step" in line_str.lower():
                # Extract progress
                yield 50.0  # Placeholder

        await process.wait()
        yield 100.0

    async def _run_gs_simulation(self) -> AsyncGenerator[float, None]:
        """Simulate 3DGS training for testing without GPU"""
        total_steps = 20

        for step in range(total_steps + 1):
            await asyncio.sleep(0.5)  # Simulate processing time
            progress = (step / total_steps) * 100
            yield progress

    def _replace_sparse_with_dense(self, fused_ply_path: Path, max_points: int = 50000) -> int:
        """Replace sparse points3D with dense MVS cloud for 3DGS initialization.

        Reads COLMAP's fused.ply, downsamples to max_points, and writes
        points3D.ply in the format 3DGS's fetchPly() expects.
        3DGS checks for points3D.ply before points3D.bin, so no 3DGS code changes needed.

        Returns number of points written.
        """
        ply_data = PlyData.read(str(fused_ply_path))
        vertices = ply_data['vertex']
        num_points = len(vertices)
        print(f"[MVS] Dense cloud has {num_points} points")

        if num_points == 0:
            print("[MVS] WARNING: Dense cloud is empty, keeping sparse initialization")
            return 0

        # Extract arrays
        xyz = np.column_stack([
            np.array(vertices['x'], dtype=np.float32),
            np.array(vertices['y'], dtype=np.float32),
            np.array(vertices['z'], dtype=np.float32),
        ])
        rgb = np.column_stack([
            np.array(vertices['red'], dtype=np.uint8),
            np.array(vertices['green'], dtype=np.uint8),
            np.array(vertices['blue'], dtype=np.uint8),
        ])

        if 'nx' in vertices.dtype.names:
            normals = np.column_stack([
                np.array(vertices['nx'], dtype=np.float32),
                np.array(vertices['ny'], dtype=np.float32),
                np.array(vertices['nz'], dtype=np.float32),
            ])
        else:
            normals = np.zeros_like(xyz)

        # Downsample if too many points (prevents VRAM overflow on 6GB GPU)
        if num_points > max_points:
            print(f"[MVS] Downsampling from {num_points} to {max_points} points")
            indices = np.random.choice(num_points, max_points, replace=False)
            xyz = xyz[indices]
            rgb = rgb[indices]
            normals = normals[indices]
            num_points = max_points

        # Write points3D.ply in storePly format (matches 3DGS's fetchPly expectations)
        gs_sparse_0 = self.distorted_dir / "sparse" / "0"
        gs_sparse_0.mkdir(parents=True, exist_ok=True)
        output_ply_path = gs_sparse_0 / "points3D.ply"

        dtype = [('x', 'f4'), ('y', 'f4'), ('z', 'f4'),
                 ('nx', 'f4'), ('ny', 'f4'), ('nz', 'f4'),
                 ('red', 'u1'), ('green', 'u1'), ('blue', 'u1')]

        elements = np.empty(num_points, dtype=dtype)
        elements['x'] = xyz[:, 0]
        elements['y'] = xyz[:, 1]
        elements['z'] = xyz[:, 2]
        elements['nx'] = normals[:, 0]
        elements['ny'] = normals[:, 1]
        elements['nz'] = normals[:, 2]
        elements['red'] = rgb[:, 0]
        elements['green'] = rgb[:, 1]
        elements['blue'] = rgb[:, 2]

        vertex_element = PlyElement.describe(elements, 'vertex')
        PlyData([vertex_element]).write(str(output_ply_path))

        print(f"[MVS] Dense initialization written: {output_ply_path} ({num_points} points)")
        return num_points

    async def _convert_colmap_to_gs_format(self):
        """Convert COLMAP undistorted output to 3DGS input format.

        3DGS expects: source_path/images/ and source_path/sparse/0/
        The undistorter outputs: distorted/images/ and distorted/sparse/
        So we need to move sparse files into a 0/ subdirectory.
        """
        print(f"[3DGS] Converting COLMAP format. distorted_dir={self.distorted_dir}")
        # Create sparse/0/ subdirectory that 3DGS expects
        gs_sparse_0 = self.distorted_dir / "sparse" / "0"
        if not gs_sparse_0.exists():
            sparse_dir = self.distorted_dir / "sparse"
            print(f"[3DGS] sparse_dir exists: {sparse_dir.exists()}, contents: {list(sparse_dir.iterdir()) if sparse_dir.exists() else 'N/A'}")
            if sparse_dir.exists():
                gs_sparse_0.mkdir(parents=True, exist_ok=True)
                for f in sparse_dir.iterdir():
                    if f.is_file():
                        print(f"[3DGS] Moving {f.name} to sparse/0/")
                        shutil.move(str(f), str(gs_sparse_0 / f.name))
        print(f"[3DGS] sparse/0 exists: {gs_sparse_0.exists()}, contents: {list(gs_sparse_0.iterdir()) if gs_sparse_0.exists() else 'N/A'}")

    async def _export_model(self):
        """Export the trained model to web-friendly format"""

        # Look for the output PLY file from 3DGS
        ply_files = list(self.gs_output_dir.rglob("point_cloud.ply"))

        if not ply_files:
            # Try iteration-specific files with current iteration setting
            ply_files = list(self.gs_output_dir.rglob(f"iteration_{self.gs_iterations}/point_cloud.ply"))

        if not ply_files:
            # Fallback: try any point_cloud directory
            ply_files = list(self.gs_output_dir.rglob("point_cloud/iteration_*/point_cloud.ply"))

        if ply_files:
            # Copy PLY to output directory
            output_ply = self.output_dir / "model.ply"
            shutil.copy2(ply_files[0], output_ply)

            # Create MeshLab-compatible PLY with standard (x,y,z,r,g,b) properties
            self._export_standard_ply(output_ply, self.output_dir / "model_meshlab.ply")

            # Create a simple GLTF reference for compatibility
            # Note: For true 3DGS viewing, frontend should use a splat viewer
            gltf_data = {
                "asset": {
                    "version": "2.0",
                    "generator": "3D Gaussian Splatting Pipeline"
                },
                "extensions": {
                    "gaussian_splat": {
                        "source": "model.ply"
                    }
                }
            }

            with open(self.output_dir / "model.gltf", "w") as f:
                json.dump(gltf_data, f, indent=2)
        else:
            # Create placeholder if no output found
            output_ply = self.output_dir / "model.ply"
            output_ply.touch()

            gltf_data = {
                "asset": {
                    "version": "2.0",
                    "generator": "3D Gaussian Splatting Pipeline (Placeholder)"
                }
            }

            with open(self.output_dir / "model.gltf", "w") as f:
                json.dump(gltf_data, f, indent=2)

    def _export_standard_ply(self, input_ply: Path, output_ply: Path):
        """Convert 3DGS PLY (with SH coefficients) to standard PLY (x,y,z,r,g,b) for MeshLab"""
        try:
            with open(input_ply, "rb") as f:
                data = f.read()

            # Parse header
            header_end = data.index(b"end_header\n") + len(b"end_header\n")
            header_text = data[:header_end].decode("ascii")
            lines = header_text.strip().split("\n")

            vertex_count = 0
            properties = []
            for line in lines:
                parts = line.strip().split()
                if parts[0] == "element" and parts[1] == "vertex":
                    vertex_count = int(parts[2])
                elif parts[0] == "property":
                    properties.append(parts[2])  # property name

            if vertex_count == 0:
                print("[Export] No vertices found in PLY")
                return

            prop_index = {name: i for i, name in enumerate(properties)}
            bytes_per_vertex = len(properties) * 4  # all float32
            body = data[header_end:]

            C0 = 0.28209479177387814
            has_sh = "f_dc_0" in prop_index

            # Write standard PLY
            with open(output_ply, "wb") as out:
                header = (
                    f"ply\n"
                    f"format binary_little_endian 1.0\n"
                    f"element vertex {vertex_count}\n"
                    f"property float x\n"
                    f"property float y\n"
                    f"property float z\n"
                    f"property uchar red\n"
                    f"property uchar green\n"
                    f"property uchar blue\n"
                    f"end_header\n"
                )
                out.write(header.encode("ascii"))

                for i in range(vertex_count):
                    offset = i * bytes_per_vertex
                    x = struct.unpack_from("<f", body, offset + prop_index["x"] * 4)[0]
                    y = struct.unpack_from("<f", body, offset + prop_index["y"] * 4)[0]
                    z = struct.unpack_from("<f", body, offset + prop_index["z"] * 4)[0]

                    if has_sh:
                        sh0 = struct.unpack_from("<f", body, offset + prop_index["f_dc_0"] * 4)[0]
                        sh1 = struct.unpack_from("<f", body, offset + prop_index["f_dc_1"] * 4)[0]
                        sh2 = struct.unpack_from("<f", body, offset + prop_index["f_dc_2"] * 4)[0]
                        r = int(max(0, min(255, (sh0 * C0 + 0.5) * 255)))
                        g = int(max(0, min(255, (sh1 * C0 + 0.5) * 255)))
                        b = int(max(0, min(255, (sh2 * C0 + 0.5) * 255)))
                    else:
                        r, g, b = 128, 128, 128

                    out.write(struct.pack("<fff", x, y, z))
                    out.write(struct.pack("BBB", r, g, b))

            print(f"[Export] Standard PLY written: {output_ply} ({vertex_count} vertices)")
        except Exception as e:
            print(f"[Export] Failed to create standard PLY: {e}")

    def _check_gpu(self) -> bool:
        """Check if GPU is available for COLMAP"""
        try:
            import torch
            return torch.cuda.is_available()
        except:
            return False

    def _check_gaussian_splatting_original(self) -> bool:
        """Check if original 3DGS is installed"""
        train_script = Path(self.gaussian_splatting_path) / "train.py"
        return train_script.exists()

    def _check_nerfstudio(self) -> bool:
        """Check if Nerfstudio is installed"""
        try:
            result = subprocess.run(
                ["ns-train", "--help"],
                capture_output=True,
                timeout=5
            )
            return result.returncode == 0
        except:
            return False


# Alias for backward compatibility
ReconstructionPipeline = GaussianSplattingPipeline
