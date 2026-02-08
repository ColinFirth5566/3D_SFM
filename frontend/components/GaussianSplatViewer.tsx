'use client';

import { useEffect, useRef, useState } from 'react';
import * as THREE from 'three';
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls.js';

interface GaussianSplatViewerProps {
  splatUrl: string;
  downloadUrl: string;
}

/**
 * Parse a 3DGS PLY file and extract positions + colors.
 * 3DGS PLY files store color as spherical harmonics (f_dc_0/1/2).
 * Convert SH band 0 to RGB: color = SH * C0 + 0.5, where C0 = 0.28209479
 */
async function parsePLY(buffer: ArrayBuffer) {
  const textDecoder = new TextDecoder();
  const bytes = new Uint8Array(buffer);

  // Find end of header
  let headerEnd = 0;
  for (let i = 0; i < bytes.length - 10; i++) {
    if (
      bytes[i] === 0x65 && // 'e'
      bytes[i + 1] === 0x6e && // 'n'
      bytes[i + 2] === 0x64 && // 'd'
      bytes[i + 3] === 0x5f && // '_'
      bytes[i + 4] === 0x68 && // 'h'
      bytes[i + 5] === 0x65 && // 'e'
      bytes[i + 6] === 0x61 && // 'a'
      bytes[i + 7] === 0x64 && // 'd'
      bytes[i + 8] === 0x65 && // 'e'
      bytes[i + 9] === 0x72 // 'r'
    ) {
      headerEnd = i + 10;
      // Skip past newline
      while (headerEnd < bytes.length && bytes[headerEnd] !== 0x0a) headerEnd++;
      headerEnd++;
      break;
    }
  }

  const headerText = textDecoder.decode(bytes.slice(0, headerEnd));
  const lines = headerText.split('\n');

  let vertexCount = 0;
  const properties: string[] = [];

  for (const line of lines) {
    const parts = line.trim().split(/\s+/);
    if (parts[0] === 'element' && parts[1] === 'vertex') {
      vertexCount = parseInt(parts[2]);
    } else if (parts[0] === 'property') {
      properties.push(parts[2]); // property name
    }
  }

  if (vertexCount === 0) throw new Error('No vertices found in PLY');

  // Build property index map
  const propIndex: Record<string, number> = {};
  properties.forEach((name, i) => {
    propIndex[name] = i;
  });

  // Each property is a float32 (4 bytes)
  const bytesPerVertex = properties.length * 4;
  const dataView = new DataView(buffer, headerEnd);

  const positions = new Float32Array(vertexCount * 3);
  const colors = new Float32Array(vertexCount * 3);
  const sizes = new Float32Array(vertexCount);

  const C0 = 0.28209479177387814;
  const hasColor = 'f_dc_0' in propIndex;
  const hasOpacity = 'opacity' in propIndex;
  const hasScale = 'scale_0' in propIndex;

  for (let i = 0; i < vertexCount; i++) {
    const offset = i * bytesPerVertex;

    // Position
    positions[i * 3] = dataView.getFloat32(offset + propIndex['x'] * 4, true);
    positions[i * 3 + 1] = dataView.getFloat32(offset + propIndex['y'] * 4, true);
    positions[i * 3 + 2] = dataView.getFloat32(offset + propIndex['z'] * 4, true);

    // Color from spherical harmonics
    if (hasColor) {
      const r = dataView.getFloat32(offset + propIndex['f_dc_0'] * 4, true) * C0 + 0.5;
      const g = dataView.getFloat32(offset + propIndex['f_dc_1'] * 4, true) * C0 + 0.5;
      const b = dataView.getFloat32(offset + propIndex['f_dc_2'] * 4, true) * C0 + 0.5;
      colors[i * 3] = Math.max(0, Math.min(1, r));
      colors[i * 3 + 1] = Math.max(0, Math.min(1, g));
      colors[i * 3 + 2] = Math.max(0, Math.min(1, b));
    } else {
      colors[i * 3] = 1;
      colors[i * 3 + 1] = 1;
      colors[i * 3 + 2] = 1;
    }

    // Size from opacity and scale
    if (hasOpacity && hasScale) {
      const opacity = 1 / (1 + Math.exp(-dataView.getFloat32(offset + propIndex['opacity'] * 4, true)));
      const s0 = Math.exp(dataView.getFloat32(offset + propIndex['scale_0'] * 4, true));
      const s1 = Math.exp(dataView.getFloat32(offset + propIndex['scale_1'] * 4, true));
      const s2 = Math.exp(dataView.getFloat32(offset + propIndex['scale_2'] * 4, true));
      sizes[i] = Math.cbrt(s0 * s1 * s2) * opacity * 50;
    } else {
      sizes[i] = 2.0;
    }
  }

  return { positions, colors, sizes, vertexCount };
}

export default function GaussianSplatViewer({ splatUrl, downloadUrl }: GaussianSplatViewerProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [pointCount, setPointCount] = useState(0);

  useEffect(() => {
    if (!containerRef.current) return;

    let animationId: number;
    let controls: OrbitControls | null = null;
    let renderer: THREE.WebGLRenderer | null = null;

    const init = async () => {
      try {
        const container = containerRef.current;
        if (!container) return;

        // Fetch PLY file
        const response = await fetch(splatUrl);
        if (!response.ok) throw new Error(`Download failed: ${response.status}`);
        const buffer = await response.arrayBuffer();

        if (buffer.byteLength < 100) {
          throw new Error('PLY file is empty or too small');
        }

        // Parse PLY
        const { positions, colors, vertexCount } = await parsePLY(buffer);
        setPointCount(vertexCount);

        // Scene
        const scene = new THREE.Scene();
        scene.background = new THREE.Color(0x1a1a2e);

        // Camera
        const camera = new THREE.PerspectiveCamera(
          65,
          container.clientWidth / container.clientHeight,
          0.01,
          1000
        );

        // Auto-center camera on point cloud
        const geometry = new THREE.BufferGeometry();
        geometry.setAttribute('position', new THREE.Float32BufferAttribute(positions, 3));
        geometry.setAttribute('color', new THREE.Float32BufferAttribute(colors, 3));
        geometry.computeBoundingSphere();

        const center = geometry.boundingSphere!.center;
        const radius = geometry.boundingSphere!.radius;
        camera.position.set(center.x + radius * 2, center.y + radius, center.z + radius * 2);
        camera.lookAt(center);

        // Point cloud material with size attenuation
        const material = new THREE.PointsMaterial({
          size: 0.02 * radius,
          vertexColors: true,
          sizeAttenuation: true,
          transparent: true,
          opacity: 0.9,
        });

        const points = new THREE.Points(geometry, material);
        scene.add(points);

        // Renderer
        renderer = new THREE.WebGLRenderer({ antialias: true });
        renderer.setSize(container.clientWidth, container.clientHeight);
        renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
        container.appendChild(renderer.domElement);

        // Controls
        controls = new OrbitControls(camera, renderer.domElement);
        controls.target.copy(center);
        controls.enableDamping = true;
        controls.dampingFactor = 0.1;
        controls.update();

        setLoading(false);

        // Animate
        const animate = () => {
          animationId = requestAnimationFrame(animate);
          controls?.update();
          renderer?.render(scene, camera);
        };
        animate();

        // Resize
        const handleResize = () => {
          if (!container || !renderer) return;
          const w = container.clientWidth;
          const h = container.clientHeight;
          camera.aspect = w / h;
          camera.updateProjectionMatrix();
          renderer.setSize(w, h);
        };
        window.addEventListener('resize', handleResize);

        return () => {
          window.removeEventListener('resize', handleResize);
          cancelAnimationFrame(animationId);
          controls?.dispose();
          if (container && renderer?.domElement) {
            container.removeChild(renderer.domElement);
          }
          renderer?.dispose();
          geometry.dispose();
          material.dispose();
        };
      } catch (err) {
        const msg = err instanceof Error ? err.message : String(err);
        console.error('Viewer error:', err);
        setError(`Failed to load 3D model: ${msg}`);
        setLoading(false);
      }
    };

    const cleanup = init();
    return () => {
      cleanup.then((fn) => fn?.());
    };
  }, [splatUrl]);

  const handleDownload = () => {
    window.open(downloadUrl, '_blank');
  };

  return (
    <div className="max-w-6xl mx-auto">
      <div className="bg-gray-800/50 backdrop-blur rounded-2xl p-8 shadow-2xl">
        <h2 className="text-3xl font-bold mb-6 text-center">
          Your 3D Reconstruction
        </h2>

        <div className="relative w-full h-[600px] bg-gray-900 rounded-xl overflow-hidden mb-6">
          <div ref={containerRef} className="w-full h-full" />

          {loading && (
            <div className="absolute inset-0 flex flex-col items-center justify-center bg-gray-900/80">
              <div className="w-16 h-16 border-4 border-blue-500 border-t-transparent rounded-full animate-spin mb-4"></div>
              <p className="text-xl text-white">Loading 3D Model...</p>
            </div>
          )}

          {error && (
            <div className="absolute inset-0 flex flex-col items-center justify-center bg-gray-900/80 p-8">
              <p className="text-xl text-red-400 text-center">{error}</p>
            </div>
          )}

          {!loading && !error && (
            <>
              <div className="absolute top-4 right-4 bg-black/70 text-white px-3 py-1 rounded text-sm">
                {pointCount.toLocaleString()} points
              </div>
              <div className="absolute bottom-4 left-4 bg-black/70 text-white px-4 py-2 rounded-lg text-sm">
                <p className="font-semibold mb-1">Controls:</p>
                <p>Left click + drag: Rotate</p>
                <p>Right click + drag: Pan</p>
                <p>Scroll: Zoom</p>
              </div>
            </>
          )}
        </div>

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
