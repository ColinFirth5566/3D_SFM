'use client';

import { useEffect, useRef, useState } from 'react';
import * as THREE from 'three';
import type { Viewer } from '@mkkellogg/gaussian-splats-3d';

interface GaussianSplatViewerProps {
  splatUrl: string;
  downloadUrl: string;
}

export default function GaussianSplatViewer({ splatUrl, downloadUrl }: GaussianSplatViewerProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const viewerRef = useRef<Viewer | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [loadProgress, setLoadProgress] = useState(0);

  useEffect(() => {
    if (!containerRef.current) return;

    let viewer: Viewer | null = null;
    let animationId: number;

    const initViewer = async () => {
      try {
        // Dynamic import for gaussian-splats-3d (client-side only)
        const GaussianSplats3D = await import('@mkkellogg/gaussian-splats-3d');

        const container = containerRef.current;
        if (!container) return;

        // Create Three.js scene
        const scene = new THREE.Scene();
        scene.background = new THREE.Color(0x1a1a2e);

        // Camera setup
        const camera = new THREE.PerspectiveCamera(
          65,
          container.clientWidth / container.clientHeight,
          0.1,
          500
        );
        camera.position.set(0, 0, 5);

        // Renderer setup
        const renderer = new THREE.WebGLRenderer({ antialias: true });
        renderer.setSize(container.clientWidth, container.clientHeight);
        renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
        container.appendChild(renderer.domElement);

        // Create the Gaussian Splat viewer
        viewer = new GaussianSplats3D.Viewer({
          scene,
          camera,
          renderer,
          selfDrivenMode: false,
          useBuiltInControls: true,
          ignoreDevicePixelRatio: false,
          gpuAcceleratedSort: true,
          sharedMemoryForWorkers: false,
          integerBasedSort: true,
          dynamicScene: false,
          webXRMode: GaussianSplats3D.WebXRMode.None,
          renderMode: GaussianSplats3D.RenderMode.OnChange,
          sceneRevealMode: GaussianSplats3D.SceneRevealMode.Instant,
        });

        viewerRef.current = viewer;

        // Add splat scene with progress tracking
        await viewer.addSplatScene(splatUrl, {
          splatAlphaRemovalThreshold: 5,
          showLoadingUI: false,
          progressiveLoad: true,
          onProgress: (percent: number) => {
            setLoadProgress(Math.round(percent));
          },
        });

        setLoading(false);

        // Animation loop
        const animate = () => {
          animationId = requestAnimationFrame(animate);
          if (viewer) {
            viewer.update();
            viewer.render();
          }
        };
        animate();

        // Handle resize
        const handleResize = () => {
          if (!container) return;
          const width = container.clientWidth;
          const height = container.clientHeight;
          camera.aspect = width / height;
          camera.updateProjectionMatrix();
          renderer.setSize(width, height);
        };

        window.addEventListener('resize', handleResize);

        // Cleanup function
        return () => {
          window.removeEventListener('resize', handleResize);
          cancelAnimationFrame(animationId);
          if (viewer) {
            viewer.dispose();
          }
          if (container && renderer.domElement) {
            container.removeChild(renderer.domElement);
          }
          renderer.dispose();
        };
      } catch (err) {
        console.error('Failed to load gaussian splat viewer:', err);
        setError('Failed to load 3D model. The model may be corrupted or incompatible.');
        setLoading(false);
      }
    };

    const cleanup = initViewer();

    return () => {
      cleanup.then((cleanupFn) => cleanupFn?.());
    };
  }, [splatUrl]);

  const handleDownload = () => {
    window.open(downloadUrl, '_blank');
  };

  return (
    <div className="max-w-6xl mx-auto">
      <div className="bg-gray-800/50 backdrop-blur rounded-2xl p-8 shadow-2xl">
        <h2 className="text-3xl font-bold mb-6 text-center">
          Your 3D Gaussian Splat Model
        </h2>

        {/* 3D Viewer */}
        <div className="relative w-full h-[600px] bg-gray-900 rounded-xl overflow-hidden mb-6">
          <div ref={containerRef} className="w-full h-full" />

          {/* Loading overlay */}
          {loading && (
            <div className="absolute inset-0 flex flex-col items-center justify-center bg-gray-900/80">
              <div className="w-16 h-16 border-4 border-blue-500 border-t-transparent rounded-full animate-spin mb-4"></div>
              <p className="text-xl text-white">Loading 3D Model...</p>
              <p className="text-lg text-gray-400 mt-2">{loadProgress}%</p>
            </div>
          )}

          {/* Error overlay */}
          {error && (
            <div className="absolute inset-0 flex flex-col items-center justify-center bg-gray-900/80">
              <p className="text-xl text-red-400">{error}</p>
            </div>
          )}

          {/* Controls hint */}
          {!loading && !error && (
            <div className="absolute bottom-4 left-4 bg-black/70 text-white px-4 py-2 rounded-lg text-sm">
              <p className="font-semibold mb-1">Controls:</p>
              <p>Left click + drag: Rotate</p>
              <p>Right click + drag: Pan</p>
              <p>Scroll: Zoom</p>
            </div>
          )}
        </div>

        {/* Download button */}
        <div className="text-center space-x-4">
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
