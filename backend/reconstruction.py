import subprocess
import os
from pathlib import Path
from typing import AsyncGenerator, Tuple
import asyncio
import shutil
import numpy as np
from PIL import Image


class MeshReconstructionPipeline:
    """
    Handles the 3D reconstruction pipeline using COLMAP MVS + Poisson Meshing.

    Pipeline stages:
    1. COLMAP - Structure from Motion for camera poses
    2. COLMAP MVS - Dense depth maps and point cloud
    3. Poisson Meshing - Vertex-colored triangle mesh
    4. Export - Convert mesh PLY to GLB for web viewer
    """

    def __init__(self, job_id: str, upload_dir: Path, output_dir: Path, fast_mode: bool = True):
        self.job_id = job_id
        self.input_dir = upload_dir / job_id
        self.output_dir = output_dir / job_id
        self.output_dir.mkdir(exist_ok=True)
        self.fast_mode = fast_mode

        # Binary paths
        self.colmap_bin = os.getenv("COLMAP_BIN", "colmap")

        # Fast mode settings
        if self.fast_mode:
            self.max_image_size = 1000
            self.sift_max_features = 8192
        else:
            self.max_image_size = 1920
            self.sift_max_features = 8192

        # Working directories
        self.colmap_dir = self.output_dir / "colmap"
        self.sparse_dir = self.colmap_dir / "sparse" / "0"
        self.distorted_dir = self.colmap_dir / "distorted"

        for d in [self.colmap_dir, self.sparse_dir, self.distorted_dir]:
            d.mkdir(exist_ok=True, parents=True)

        # Copy images to colmap input directory
        self.images_dir = self.colmap_dir / "input"
        self.images_dir.mkdir(exist_ok=True)

    async def run(self) -> AsyncGenerator[Tuple[int, str], None]:
        """
        Run the complete mesh reconstruction pipeline.
        Yields progress updates as (progress_percentage, stage_description).
        """
        try:
            implementation = os.getenv("GS_IMPLEMENTATION", "auto")
            is_simulation = implementation == "simulation"

            # Step 1: Prepare images (0-5%)
            yield 2, "Preparing images..."
            await self._prepare_images()
            yield 5, "Images prepared"

            if not is_simulation:
                # Step 2: Feature extraction (5-15%)
                yield 8, "Extracting features with COLMAP..."
                await self._run_colmap_feature_extraction()
                yield 15, "Features extracted"

                # Step 3: Feature matching (15-25%)
                yield 18, "Matching features..."
                await self._run_colmap_matching()
                yield 25, "Features matched"

                # Step 4: SfM mapper (25-35%)
                yield 28, "Computing camera poses (SfM)..."
                await self._run_colmap_mapper()
                yield 35, "Camera poses computed"

                # Step 5: Undistortion (35-40%)
                yield 36, "Undistorting images..."
                await self._run_colmap_undistortion()
                yield 40, "Images undistorted"

                # Step 6: PatchMatch MVS (40-65%)
                yield 42, "Computing dense depth maps (PatchMatch MVS)..."
                await self._run_colmap_patch_match_stereo()
                yield 65, "Dense depth maps computed"

                # Step 7: Stereo fusion (65-75%)
                yield 67, "Fusing dense point cloud..."
                fused_ply = await self._run_colmap_stereo_fusion()
                yield 75, "Dense point cloud fused"

                # Step 8: Poisson meshing (75-85%)
                yield 77, "Generating triangle mesh (Poisson mesher)..."
                mesh_ply = await self._run_poisson_mesher()
                yield 85, "Triangle mesh generated"

                # Step 9: Convert to GLB (85-95%)
                yield 87, "Converting mesh to GLB for web viewer..."
                await self._convert_mesh_to_glb(mesh_ply)
                yield 95, "GLB model ready"

            else:
                # Simulation mode
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
                yield 40, "Images undistorted (simulated)"

                yield 42, "Simulating dense reconstruction..."
                await asyncio.sleep(1.0)
                yield 75, "Dense reconstruction simulated"

                yield 77, "Simulating mesh generation..."
                await asyncio.sleep(0.5)
                yield 85, "Mesh generated (simulated)"

                yield 87, "Creating placeholder GLB..."
                await self._create_simulation_glb()
                yield 95, "GLB model ready (simulated)"

            # Step 10: Finalize (95-100%)
            yield 97, "Finalizing output..."
            await self._finalize_output()
            yield 100, "Model ready"

        except Exception as e:
            raise Exception(f"Mesh reconstruction failed: {str(e)}")

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

                try:
                    with Image.open(img) as pil_img:
                        if pil_img.mode != 'RGB':
                            pil_img = pil_img.convert('RGB')

                        width, height = pil_img.size
                        max_dim = max(width, height)

                        if max_dim > self.max_image_size:
                            scale = self.max_image_size / max_dim
                            new_width = int(width * scale)
                            new_height = int(height * scale)
                            pil_img = pil_img.resize((new_width, new_height), Image.LANCZOS)

                        dest_jpg = self.images_dir / f"{img.stem}.jpg"
                        pil_img.save(dest_jpg, "JPEG", quality=90)
                except Exception:
                    shutil.copy2(img, dest)

    async def _run_colmap_feature_extraction(self):
        """Extract features using COLMAP"""
        database_path = self.colmap_dir / "database.db"

        command = [
            self.colmap_bin,
            "feature_extractor",
            "--database_path", str(database_path),
            "--image_path", str(self.images_dir),
            "--ImageReader.camera_model", "OPENCV",
            "--FeatureExtraction.use_gpu", "1" if self._check_gpu() else "0",
            "--SiftExtraction.max_num_features", str(self.sift_max_features),
            "--FeatureExtraction.num_threads", "-1",
        ]

        await self._run_command(command, "COLMAP feature extraction failed")

    async def _run_colmap_matching(self):
        """Match features using COLMAP"""
        database_path = self.colmap_dir / "database.db"

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
        """Undistort images for MVS"""
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
                "--PatchMatchStereo.window_radius", "5",
                "--PatchMatchStereo.num_iterations", "3",
            ])

        await self._run_command(command, "COLMAP PatchMatchStereo failed")

    async def _run_colmap_stereo_fusion(self) -> Path:
        """Run COLMAP stereo fusion to create dense point cloud."""
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

    async def _run_poisson_mesher(self) -> Path:
        """Run COLMAP Poisson mesher to create a vertex-colored triangle mesh."""
        mesh_ply_path = self.distorted_dir / "meshed-poisson.ply"

        poisson_depth = 9 if self.fast_mode else 11

        command = [
            self.colmap_bin,
            "poisson_mesher",
            "--input_path", str(self.distorted_dir / "fused.ply"),
            "--output_path", str(mesh_ply_path),
            "--PoissonMeshing.depth", str(poisson_depth),
            "--PoissonMeshing.trim", "7",
        ]

        await self._run_command(command, "COLMAP Poisson mesher failed")

        if not mesh_ply_path.exists():
            raise Exception("Poisson mesher completed but meshed-poisson.ply not found")

        print(f"[Mesh] Poisson mesh: {mesh_ply_path} ({mesh_ply_path.stat().st_size} bytes)")
        return mesh_ply_path

    async def _convert_mesh_to_glb(self, mesh_ply_path: Path):
        """Convert the Poisson mesh PLY to GLB using trimesh."""
        import trimesh

        mesh = trimesh.load(str(mesh_ply_path), process=False)
        print(f"[Export] Loaded mesh: {len(mesh.vertices)} vertices, {len(mesh.faces)} faces")

        # Copy mesh PLY to output directory for download
        output_mesh_ply = self.output_dir / "model.ply"
        shutil.copy2(mesh_ply_path, output_mesh_ply)

        # Export as GLB
        output_glb = self.output_dir / "model.glb"
        mesh.export(str(output_glb), file_type="glb")
        print(f"[Export] GLB written: {output_glb} ({output_glb.stat().st_size} bytes)")

    async def _create_simulation_glb(self):
        """Create a placeholder GLB for simulation mode."""
        import trimesh

        # Create a simple colored box as placeholder
        mesh = trimesh.creation.box(extents=[1, 1, 1])
        mesh.visual.vertex_colors = np.tile([100, 150, 200, 255], (len(mesh.vertices), 1)).astype(np.uint8)

        output_glb = self.output_dir / "model.glb"
        mesh.export(str(output_glb), file_type="glb")

        # Also create a placeholder PLY
        output_ply = self.output_dir / "model.ply"
        mesh.export(str(output_ply), file_type="ply")

        print(f"[Simulation] Placeholder GLB and PLY created")

    async def _finalize_output(self):
        """Verify output files exist."""
        glb_path = self.output_dir / "model.glb"
        ply_path = self.output_dir / "model.ply"

        if not glb_path.exists():
            raise Exception("GLB output file not found")
        if not ply_path.exists():
            raise Exception("PLY output file not found")

        print(f"[Finalize] GLB: {glb_path.stat().st_size} bytes, PLY: {ply_path.stat().st_size} bytes")

    def _check_gpu(self) -> bool:
        """Check if GPU is available for COLMAP"""
        try:
            import torch
            return torch.cuda.is_available()
        except Exception:
            return False


# Aliases for backward compatibility
GaussianSplattingPipeline = MeshReconstructionPipeline
ReconstructionPipeline = MeshReconstructionPipeline
