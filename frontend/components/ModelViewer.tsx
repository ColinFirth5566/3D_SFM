'use client';

import { Suspense, useRef } from 'react';
import { Canvas, useFrame } from '@react-three/fiber';
import { OrbitControls, useGLTF, PerspectiveCamera, Environment } from '@react-three/drei';
import * as THREE from 'three';

interface ModelProps {
  url: string;
}

function Model({ url }: ModelProps) {
  const { scene } = useGLTF(url);
  const modelRef = useRef<THREE.Group>(null);

  // Center and scale the model
  useFrame(() => {
    if (modelRef.current) {
      const box = new THREE.Box3().setFromObject(modelRef.current);
      const center = box.getCenter(new THREE.Vector3());
      const size = box.getSize(new THREE.Vector3());
      const maxDim = Math.max(size.x, size.y, size.z);
      const scale = 5 / maxDim;

      modelRef.current.scale.setScalar(scale);
      modelRef.current.position.sub(center.multiplyScalar(scale));
    }
  });

  return <primitive ref={modelRef} object={scene} />;
}

interface ModelViewerProps {
  modelUrl: string;
}

export default function ModelViewer({ modelUrl }: ModelViewerProps) {
  const handleDownload = () => {
    window.open(modelUrl, '_blank');
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
            <PerspectiveCamera makeDefault position={[0, 0, 10]} />
            <ambientLight intensity={0.5} />
            <directionalLight position={[10, 10, 5]} intensity={1} />
            <directionalLight position={[-10, -10, -5]} intensity={0.5} />

            <Suspense fallback={null}>
              <Model url={modelUrl} />
              <Environment preset="studio" />
            </Suspense>

            <OrbitControls
              enableDamping
              dampingFactor={0.05}
              rotateSpeed={0.5}
              minDistance={2}
              maxDistance={20}
            />
            <gridHelper args={[20, 20]} />
          </Canvas>

          {/* Controls hint */}
          <div className="absolute bottom-4 left-4 bg-black/70 text-white px-4 py-2 rounded-lg text-sm">
            <p className="font-semibold mb-1">Controls:</p>
            <p>🖱️ Left click + drag: Rotate</p>
            <p>🖱️ Right click + drag: Pan</p>
            <p>🔄 Scroll: Zoom</p>
          </div>
        </div>

        {/* Download button */}
        <div className="text-center">
          <button
            onClick={handleDownload}
            className="bg-gradient-to-r from-green-600 to-blue-600 hover:from-green-700 hover:to-blue-700 text-white font-bold py-4 px-12 rounded-lg text-lg transition duration-200 shadow-lg"
          >
            ⬇️ Download GLTF Model
          </button>
        </div>
      </div>
    </div>
  );
}
