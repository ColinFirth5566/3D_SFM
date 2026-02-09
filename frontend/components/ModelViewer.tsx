'use client';

import { Suspense, useEffect, useRef, useState } from 'react';
import { Canvas, useThree } from '@react-three/fiber';
import { OrbitControls, useGLTF, PerspectiveCamera } from '@react-three/drei';
import * as THREE from 'three';

interface ModelProps {
  url: string;
  onLoaded?: (info: { vertices: number; faces: number }) => void;
}

function Model({ url, onLoaded }: ModelProps) {
  const { scene } = useGLTF(url);
  const { camera } = useThree();
  const groupRef = useRef<THREE.Group>(null);
  const [centered, setCentered] = useState(false);

  // Enable vertex colors on all mesh materials and gather stats
  useEffect(() => {
    let totalVertices = 0;
    let totalFaces = 0;

    scene.traverse((child) => {
      if ((child as THREE.Mesh).isMesh) {
        const mesh = child as THREE.Mesh;
        totalVertices += mesh.geometry.attributes.position?.count ?? 0;
        totalFaces += mesh.geometry.index
          ? mesh.geometry.index.count / 3
          : (mesh.geometry.attributes.position?.count ?? 0) / 3;

        // Enable vertex colors if the geometry has them
        if (mesh.geometry.attributes.color) {
          const mat = mesh.material as THREE.MeshStandardMaterial;
          mat.vertexColors = true;
          mat.needsUpdate = true;
        }
      }
    });

    onLoaded?.({ vertices: Math.round(totalVertices), faces: Math.round(totalFaces) });
  }, [scene, onLoaded]);

  // Auto-center and scale the model once
  useEffect(() => {
    if (centered) return;
    const box = new THREE.Box3().setFromObject(scene);
    const center = box.getCenter(new THREE.Vector3());
    const size = box.getSize(new THREE.Vector3());
    const maxDim = Math.max(size.x, size.y, size.z);

    if (maxDim === 0) return;

    const scale = 5 / maxDim;
    scene.scale.setScalar(scale);
    scene.position.copy(center.multiplyScalar(-scale));

    // Position camera
    const cam = camera as THREE.PerspectiveCamera;
    cam.position.set(6, 4, 6);
    cam.lookAt(0, 0, 0);

    setCentered(true);
  }, [scene, camera, centered]);

  return <primitive ref={groupRef} object={scene} />;
}

interface ModelViewerProps {
  modelUrl: string;
  downloadUrl: string;
}

export default function ModelViewer({ modelUrl, downloadUrl }: ModelViewerProps) {
  const [info, setInfo] = useState<{ vertices: number; faces: number } | null>(null);

  const handleDownload = () => {
    window.open(downloadUrl, '_blank');
  };

  return (
    <div className="max-w-6xl mx-auto">
      <div className="bg-gray-800/50 backdrop-blur rounded-2xl p-8 shadow-2xl">
        <h2 className="text-3xl font-bold mb-6 text-center">
          Your 3D Model
        </h2>

        {/* 3D Viewer */}
        <div className="relative w-full h-[600px] bg-gray-900 rounded-xl overflow-hidden mb-6">
          <Canvas>
            <PerspectiveCamera makeDefault position={[6, 4, 6]} />
            <ambientLight intensity={0.6} />
            <directionalLight position={[10, 10, 5]} intensity={1} />
            <directionalLight position={[-10, -10, -5]} intensity={0.4} />

            <Suspense fallback={null}>
              <Model url={modelUrl} onLoaded={setInfo} />
            </Suspense>

            <OrbitControls
              enableDamping
              dampingFactor={0.05}
              rotateSpeed={0.5}
              minDistance={1}
              maxDistance={30}
            />
            <gridHelper args={[20, 20, '#444444', '#333333']} />
          </Canvas>

          {/* Stats */}
          {info && (
            <div className="absolute top-4 right-4 bg-black/70 text-white px-3 py-1 rounded text-sm">
              {info.vertices.toLocaleString()} vertices &middot; {info.faces.toLocaleString()} faces
            </div>
          )}

          {/* Controls hint */}
          <div className="absolute bottom-4 left-4 bg-black/70 text-white px-4 py-2 rounded-lg text-sm">
            <p className="font-semibold mb-1">Controls:</p>
            <p>Left click + drag: Rotate</p>
            <p>Right click + drag: Pan</p>
            <p>Scroll: Zoom</p>
          </div>
        </div>

        {/* Download button */}
        <div className="text-center">
          <button
            onClick={handleDownload}
            className="bg-gradient-to-r from-green-600 to-blue-600 hover:from-green-700 hover:to-blue-700 text-white font-bold py-4 px-12 rounded-lg text-lg transition duration-200 shadow-lg"
          >
            Download PLY Model
          </button>
        </div>
      </div>
    </div>
  );
}
