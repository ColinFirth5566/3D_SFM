import subprocess
import os
from pathlib import Path
from typing import AsyncGenerator, Tuple
import asyncio
import json


class ReconstructionPipeline:
    """
    Handles the 3D reconstruction pipeline using OpenMVG and OpenMVS
    """

    def __init__(self, job_id: str, upload_dir: Path, output_dir: Path):
        self.job_id = job_id
        self.input_dir = upload_dir / job_id
        self.output_dir = output_dir / job_id
        self.output_dir.mkdir(exist_ok=True)

        # OpenMVG paths - these need to be configured based on installation
        self.openmvg_bin = os.getenv("OPENMVG_BIN", "/usr/local/bin")
        self.openmvs_bin = os.getenv("OPENMVS_BIN", "/usr/local/bin")

        # Working directories
        self.matches_dir = self.output_dir / "matches"
        self.reconstruction_dir = self.output_dir / "reconstruction"
        self.mvs_dir = self.output_dir / "mvs"

        for dir in [self.matches_dir, self.reconstruction_dir, self.mvs_dir]:
            dir.mkdir(exist_ok=True)

    async def run(self) -> AsyncGenerator[Tuple[int, str], None]:
        """
        Run the complete reconstruction pipeline
        Yields progress updates as (progress_percentage, stage_description)
        """

        try:
            # Step 1: Image listing (0-10%)
            yield 5, "Analyzing images..."
            await self._run_image_listing()
            yield 10, "Images analyzed"

            # Step 2: Feature extraction (10-30%)
            yield 15, "Extracting features..."
            await self._run_feature_extraction()
            yield 30, "Features extracted"

            # Step 3: Feature matching (30-50%)
            yield 35, "Matching features..."
            await self._run_feature_matching()
            yield 50, "Features matched"

            # Step 4: Structure from Motion (50-70%)
            yield 55, "Computing structure from motion..."
            await self._run_sfm()
            yield 70, "Structure computed"

            # Step 5: Dense reconstruction with OpenMVS (70-90%)
            yield 75, "Creating dense point cloud..."
            await self._run_dense_reconstruction()
            yield 90, "Dense reconstruction complete"

            # Step 6: Export to GLTF (90-100%)
            yield 95, "Generating 3D model..."
            await self._export_to_gltf()
            yield 100, "Model ready"

        except Exception as e:
            raise Exception(f"Reconstruction failed: {str(e)}")

    async def _run_command(self, command: list, error_msg: str):
        """Run a subprocess command asynchronously"""
        process = await asyncio.create_subprocess_exec(
            *command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )

        stdout, stderr = await process.communicate()

        if process.returncode != 0:
            raise Exception(f"{error_msg}: {stderr.decode()}")

        return stdout.decode()

    async def _run_image_listing(self):
        """Create image listing for OpenMVG"""
        # For now, create a simple image list
        # In production, use OpenMVG's SfM_Data_Init
        images = sorted(self.input_dir.glob("*.*"))

        sfm_data = {
            "root_path": str(self.input_dir),
            "views": [],
            "intrinsics": [],
            "extrinsics": []
        }

        for idx, img_path in enumerate(images):
            sfm_data["views"].append({
                "key": idx,
                "value": {
                    "polymorphic_id": 1073741824,
                    "ptr_wrapper": {
                        "id": idx,
                        "data": {
                            "local_path": img_path.name,
                            "filename": img_path.name,
                            "width": 1920,
                            "height": 1080,
                            "id_view": idx,
                            "id_intrinsic": 0,
                            "id_pose": idx
                        }
                    }
                }
            })

        with open(self.matches_dir / "sfm_data.json", "w") as f:
            json.dump(sfm_data, f, indent=2)

    async def _run_feature_extraction(self):
        """Extract features using OpenMVG"""
        # Simulate feature extraction for now
        # In production, call: openMVG_main_SfMInit_ImageListing
        # and openMVG_main_ComputeFeatures
        await asyncio.sleep(2)  # Simulate processing

    async def _run_feature_matching(self):
        """Match features using OpenMVG"""
        # Simulate feature matching for now
        # In production, call: openMVG_main_ComputeMatches
        await asyncio.sleep(2)  # Simulate processing

    async def _run_sfm(self):
        """Run Structure from Motion"""
        # Simulate SfM for now
        # In production, call: openMVG_main_IncrementalSfM
        await asyncio.sleep(3)  # Simulate processing

    async def _run_dense_reconstruction(self):
        """Run dense reconstruction with OpenMVS"""
        # Simulate dense reconstruction for now
        # In production, convert OpenMVG to OpenMVS format and run:
        # - DensifyPointCloud
        # - ReconstructMesh
        # - RefineMesh
        # - TextureMesh
        await asyncio.sleep(3)  # Simulate processing

    async def _export_to_gltf(self):
        """Export the reconstructed model to GLTF format"""
        # Create a simple placeholder GLTF file for testing
        # In production, convert the OpenMVS mesh to GLTF using a converter

        gltf_data = {
            "asset": {
                "version": "2.0",
                "generator": "3D Reconstruction Pipeline"
            },
            "scene": 0,
            "scenes": [
                {
                    "nodes": [0]
                }
            ],
            "nodes": [
                {
                    "mesh": 0
                }
            ],
            "meshes": [
                {
                    "primitives": [
                        {
                            "attributes": {
                                "POSITION": 0
                            },
                            "indices": 1
                        }
                    ]
                }
            ],
            "buffers": [],
            "bufferViews": [],
            "accessors": []
        }

        output_file = self.output_dir / "model.gltf"
        with open(output_file, "w") as f:
            json.dump(gltf_data, f, indent=2)

        # Note: This is a placeholder. In production, you would:
        # 1. Use OpenMVS to generate a mesh (PLY or OBJ format)
        # 2. Convert the mesh to GLTF using a tool like obj2gltf or assimp
        # 3. Ensure textures are properly embedded or referenced
