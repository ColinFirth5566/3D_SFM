'use client';

import { useEffect, useState } from 'react';
import { API_ENDPOINTS } from '@/lib/config';

interface ReconstructionProgressProps {
  jobId: string;
  onComplete: (jobId: string) => void;
  onError: () => void;
}

export default function ReconstructionProgress({
  jobId,
  onComplete,
  onError,
}: ReconstructionProgressProps) {
  const [progress, setProgress] = useState(0);
  const [stage, setStage] = useState('Initializing...');

  useEffect(() => {
    const checkStatus = async () => {
      try {
        const response = await fetch(API_ENDPOINTS.status(jobId));

        if (!response.ok) {
          throw new Error('Status check failed');
        }

        const data = await response.json();

        setProgress(data.progress);
        setStage(data.stage);

        if (data.status === 'completed') {
          onComplete(jobId);
        } else if (data.status === 'failed') {
          onError();
        }
      } catch (error) {
        console.error('Status check error:', error);
        onError();
      }
    };

    const interval = setInterval(checkStatus, 2000); // Check every 2 seconds

    return () => clearInterval(interval);
  }, [jobId, onComplete, onError]);

  return (
    <div className="max-w-2xl mx-auto">
      <div className="bg-gray-800/50 backdrop-blur rounded-2xl p-8 shadow-2xl">
        <h2 className="text-3xl font-bold mb-8 text-center">
          Reconstructing Your 3D Model
        </h2>

        {/* Animated 3D cube */}
        <div className="flex justify-center mb-8">
          <div className="relative w-24 h-24">
            <div className="absolute inset-0 animate-spin-slow">
              <div className="w-full h-full border-4 border-blue-500 border-opacity-50 rotate-45"></div>
            </div>
            <div className="absolute inset-0 animate-spin-slower">
              <div className="w-full h-full border-4 border-purple-500 border-opacity-50 -rotate-45"></div>
            </div>
          </div>
        </div>

        {/* Progress bar */}
        <div className="mb-6">
          <div className="flex justify-between mb-2">
            <span className="text-sm font-medium">{stage}</span>
            <span className="text-sm font-medium">{progress}%</span>
          </div>
          <div className="w-full bg-gray-700 rounded-full h-4 overflow-hidden">
            <div
              className="h-full bg-gradient-to-r from-blue-500 to-purple-500 transition-all duration-500 ease-out rounded-full"
              style={{ width: `${progress}%` }}
            >
              <div className="h-full w-full animate-pulse opacity-50 bg-white"></div>
            </div>
          </div>
        </div>

        {/* Stage descriptions matching mesh pipeline */}
        <div className="space-y-3 text-sm text-gray-300">
          <div className={`flex items-center ${progress >= 5 ? 'text-white' : ''}`}>
            <div className={`w-2 h-2 rounded-full mr-3 ${progress >= 5 ? 'bg-green-500' : progress >= 0 ? 'bg-blue-500 animate-pulse' : 'bg-gray-600'}`}></div>
            <span>Feature extraction &amp; matching</span>
          </div>
          <div className={`flex items-center ${progress >= 25 ? 'text-white' : ''}`}>
            <div className={`w-2 h-2 rounded-full mr-3 ${progress >= 35 ? 'bg-green-500' : progress >= 25 ? 'bg-blue-500 animate-pulse' : 'bg-gray-600'}`}></div>
            <span>Structure from Motion (camera poses)</span>
          </div>
          <div className={`flex items-center ${progress >= 40 ? 'text-white' : ''}`}>
            <div className={`w-2 h-2 rounded-full mr-3 ${progress >= 75 ? 'bg-green-500' : progress >= 40 ? 'bg-blue-500 animate-pulse' : 'bg-gray-600'}`}></div>
            <span>Multi-View Stereo dense reconstruction</span>
          </div>
          <div className={`flex items-center ${progress >= 75 ? 'text-white' : ''}`}>
            <div className={`w-2 h-2 rounded-full mr-3 ${progress >= 85 ? 'bg-green-500' : progress >= 75 ? 'bg-blue-500 animate-pulse' : 'bg-gray-600'}`}></div>
            <span>Mesh generation (Poisson surface)</span>
          </div>
          <div className={`flex items-center ${progress >= 85 ? 'text-white' : ''}`}>
            <div className={`w-2 h-2 rounded-full mr-3 ${progress >= 100 ? 'bg-green-500' : progress >= 85 ? 'bg-blue-500 animate-pulse' : 'bg-gray-600'}`}></div>
            <span>Model export</span>
          </div>
        </div>

        <p className="text-center text-gray-400 mt-8 text-sm">
          Processing typically completes in under 5 minutes for 12 images...
        </p>
      </div>
    </div>
  );
}
