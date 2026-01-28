'use client';

import { useState } from 'react';
import ImageUpload from '@/components/ImageUpload';
import ReconstructionProgress from '@/components/ReconstructionProgress';
import ModelViewer from '@/components/ModelViewer';

export default function Home() {
  const [jobId, setJobId] = useState<string | null>(null);
  const [modelUrl, setModelUrl] = useState<string | null>(null);
  const [status, setStatus] = useState<'idle' | 'uploading' | 'processing' | 'complete' | 'error'>('idle');

  const handleUploadComplete = (newJobId: string) => {
    setJobId(newJobId);
    setStatus('processing');
  };

  const handleReconstructionComplete = (url: string) => {
    setModelUrl(url);
    setStatus('complete');
  };

  const handleError = () => {
    setStatus('error');
  };

  const resetApp = () => {
    setJobId(null);
    setModelUrl(null);
    setStatus('idle');
  };

  return (
    <main className="min-h-screen bg-gradient-to-br from-gray-900 via-blue-900 to-gray-900 text-white">
      <div className="container mx-auto px-4 py-8">
        <header className="text-center mb-12">
          <h1 className="text-5xl font-bold mb-4 bg-clip-text text-transparent bg-gradient-to-r from-blue-400 to-purple-400">
            3D Reconstruction Studio
          </h1>
          <p className="text-xl text-gray-300">
            Transform your photos into interactive 3D models
          </p>
        </header>

        {status === 'idle' && (
          <ImageUpload onUploadComplete={handleUploadComplete} onError={handleError} />
        )}

        {status === 'uploading' && (
          <div className="text-center">
            <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-white mx-auto"></div>
            <p className="mt-4 text-xl">Uploading images...</p>
          </div>
        )}

        {status === 'processing' && jobId && (
          <ReconstructionProgress
            jobId={jobId}
            onComplete={handleReconstructionComplete}
            onError={handleError}
          />
        )}

        {status === 'complete' && modelUrl && (
          <div>
            <ModelViewer modelUrl={modelUrl} />
            <div className="text-center mt-8">
              <button
                onClick={resetApp}
                className="bg-blue-600 hover:bg-blue-700 text-white font-bold py-3 px-8 rounded-lg transition duration-200"
              >
                Create Another Model
              </button>
            </div>
          </div>
        )}

        {status === 'error' && (
          <div className="text-center">
            <div className="bg-red-900/50 border border-red-500 rounded-lg p-8 max-w-md mx-auto">
              <h2 className="text-2xl font-bold mb-4">Error</h2>
              <p className="mb-6">An error occurred during reconstruction. Please try again.</p>
              <button
                onClick={resetApp}
                className="bg-blue-600 hover:bg-blue-700 text-white font-bold py-3 px-8 rounded-lg transition duration-200"
              >
                Try Again
              </button>
            </div>
          </div>
        )}
      </div>
    </main>
  );
}
