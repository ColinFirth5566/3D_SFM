'use client';

import { useState, useCallback } from 'react';
import { useDropzone } from 'react-dropzone';

interface ImageUploadProps {
  onUploadComplete: (jobId: string) => void;
  onError: () => void;
}

export default function ImageUpload({ onUploadComplete, onError }: ImageUploadProps) {
  const [files, setFiles] = useState<File[]>([]);
  const [uploading, setUploading] = useState(false);

  const onDrop = useCallback((acceptedFiles: File[]) => {
    const imageFiles = acceptedFiles.filter(file =>
      file.type === 'image/png' || file.type === 'image/jpeg'
    );
    setFiles(prev => [...prev, ...imageFiles].slice(0, 20)); // Max 20 images
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'image/png': ['.png'],
      'image/jpeg': ['.jpg', '.jpeg']
    },
    maxFiles: 20
  });

  const removeFile = (index: number) => {
    setFiles(prev => prev.filter((_, i) => i !== index));
  };

  const handleUpload = async () => {
    if (files.length < 10) {
      alert('Please upload at least 10 images');
      return;
    }

    setUploading(true);

    const formData = new FormData();
    files.forEach((file) => {
      formData.append('files', file);
    });

    try {
      const response = await fetch('http://localhost:8000/api/upload', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        throw new Error('Upload failed');
      }

      const data = await response.json();
      onUploadComplete(data.job_id);
    } catch (error) {
      console.error('Upload error:', error);
      onError();
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto">
      <div
        {...getRootProps()}
        className={`border-4 border-dashed rounded-xl p-12 text-center cursor-pointer transition-all duration-200 ${
          isDragActive
            ? 'border-blue-400 bg-blue-900/20'
            : 'border-gray-600 hover:border-gray-500 bg-gray-800/50'
        }`}
      >
        <input {...getInputProps()} />
        <div className="space-y-4">
          <svg
            className="mx-auto h-16 w-16 text-gray-400"
            stroke="currentColor"
            fill="none"
            viewBox="0 0 48 48"
          >
            <path
              d="M28 8H12a4 4 0 00-4 4v20m32-12v8m0 0v8a4 4 0 01-4 4H12a4 4 0 01-4-4v-4m32-4l-3.172-3.172a4 4 0 00-5.656 0L28 28M8 32l9.172-9.172a4 4 0 015.656 0L28 28m0 0l4 4m4-24h8m-4-4v8m-12 4h.02"
              strokeWidth={2}
              strokeLinecap="round"
              strokeLinejoin="round"
            />
          </svg>
          {isDragActive ? (
            <p className="text-xl">Drop images here...</p>
          ) : (
            <div>
              <p className="text-xl mb-2">Drag and drop images here, or click to select</p>
              <p className="text-sm text-gray-400">
                Upload 10-20 photos (PNG or JPG, max 1080p)
              </p>
            </div>
          )}
        </div>
      </div>

      {files.length > 0 && (
        <div className="mt-8">
          <h3 className="text-xl font-semibold mb-4">
            Selected Images ({files.length}/20)
          </h3>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
            {files.map((file, index) => (
              <div key={index} className="relative group">
                <img
                  src={URL.createObjectURL(file)}
                  alt={`Preview ${index + 1}`}
                  className="w-full h-32 object-cover rounded-lg"
                />
                <button
                  onClick={() => removeFile(index)}
                  className="absolute top-2 right-2 bg-red-600 hover:bg-red-700 text-white rounded-full w-6 h-6 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity"
                >
                  ×
                </button>
                <p className="text-xs text-gray-400 mt-1 truncate">{file.name}</p>
              </div>
            ))}
          </div>

          <div className="text-center">
            <button
              onClick={handleUpload}
              disabled={uploading || files.length < 10}
              className={`text-white font-bold py-4 px-12 rounded-lg text-lg transition duration-200 ${
                uploading || files.length < 10
                  ? 'bg-gray-600 cursor-not-allowed'
                  : 'bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700'
              }`}
            >
              {uploading ? 'Uploading...' : `Start Reconstruction (${files.length} images)`}
            </button>
            {files.length < 10 && (
              <p className="text-yellow-400 mt-2">
                Please upload at least {10 - files.length} more image(s)
              </p>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
