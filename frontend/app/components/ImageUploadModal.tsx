'use client';

import { useState } from 'react';

interface ImageUploadModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (images: { front: File | null; left: File | null; right: File | null }) => void;
}

export default function ImageUploadModal({ isOpen, onClose, onSubmit }: ImageUploadModalProps) {
  const [images, setImages] = useState<{
    front: File | null;
    left: File | null;
    right: File | null;
  }>({
    front: null,
    left: null,
    right: null,
  });
  const [uploading, setUploading] = useState(false);

  if (!isOpen) return null;

  const handleImageSelect = (type: 'front' | 'left' | 'right', file: File) => {
    setImages((prev) => ({ ...prev, [type]: file }));
  };

  const handleImageClick = (type: 'front' | 'left' | 'right') => {
    const input = document.createElement('input');
    input.type = 'file';
    input.accept = 'image/*';
    input.onchange = (e) => {
      const file = (e.target as HTMLInputElement).files?.[0];
      if (file) {
        handleImageSelect(type, file);
      }
    };
    input.click();
  };

  const handleSubmit = async () => {
    if (!images.front || !images.left || !images.right) {
      alert('Please upload all three images (front, left, and right)');
      return;
    }
    setUploading(true);
    await onSubmit(images);
    setUploading(false);
  };

  const handleClose = () => {
    if (!uploading) {
      setImages({ front: null, left: null, right: null });
      onClose();
    }
  };

  return (
    <div className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center p-4">
      <div className="bg-gradient-to-br from-purple-900 via-gray-900 to-pink-900 rounded-3xl shadow-2xl border border-white/20 w-full max-w-4xl max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="sticky top-0 bg-black/40 backdrop-blur-xl border-b border-white/10 p-6 flex justify-between items-center">
          <h2 className="text-2xl font-bold bg-gradient-to-r from-purple-400 to-pink-400 bg-clip-text text-transparent">
            📸 Upload Body Images
          </h2>
          <button
            onClick={handleClose}
            disabled={uploading}
            className="text-gray-400 hover:text-white text-2xl transition-colors"
          >
            ✕
          </button>
        </div>

        {/* Content */}
        <div className="p-6 space-y-6">
          <p className="text-gray-300 text-center mb-6">
            Upload three images of your body (front, left, and right) to get personalized recommendations
          </p>

          {/* Upload Grid */}
          <div className="grid md:grid-cols-3 gap-6">
            {/* Front View */}
            <div className="space-y-3">
              <h3 className="text-lg font-semibold text-white text-center">Front View</h3>
              <div
                onClick={() => handleImageClick('front')}
                className="bg-white/5 hover:bg-white/10 border-2 border-dashed border-white/20 rounded-2xl p-8 cursor-pointer transition-all group hover:border-purple-500/50 min-h-[200px] flex items-center justify-center"
              >
                {images.front ? (
                  <div className="text-center space-y-2">
                    <div className="text-5xl">✅</div>
                    <p className="text-sm text-gray-400 group-hover:text-white truncate max-w-[150px]">
                      {images.front.name}
                    </p>
                  </div>
                ) : (
                  <div className="text-center space-y-3">
                    <div className="text-6xl">📷</div>
                    <p className="text-gray-400 group-hover:text-white">Click to upload</p>
                  </div>
                )}
              </div>
            </div>

            {/* Left Side */}
            <div className="space-y-3">
              <h3 className="text-lg font-semibold text-white text-center">Left Side</h3>
              <div
                onClick={() => handleImageClick('left')}
                className="bg-white/5 hover:bg-white/10 border-2 border-dashed border-white/20 rounded-2xl p-8 cursor-pointer transition-all group hover:border-purple-500/50 min-h-[200px] flex items-center justify-center"
              >
                {images.left ? (
                  <div className="text-center space-y-2">
                    <div className="text-5xl">✅</div>
                    <p className="text-sm text-gray-400 group-hover:text-white truncate max-w-[150px]">
                      {images.left.name}
                    </p>
                  </div>
                ) : (
                  <div className="text-center space-y-3">
                    <div className="text-6xl">📷</div>
                    <p className="text-gray-400 group-hover:text-white">Click to upload</p>
                  </div>
                )}
              </div>
            </div>

            {/* Right Side */}
            <div className="space-y-3">
              <h3 className="text-lg font-semibold text-white text-center">Right Side</h3>
              <div
                onClick={() => handleImageClick('right')}
                className="bg-white/5 hover:bg-white/10 border-2 border-dashed border-white/20 rounded-2xl p-8 cursor-pointer transition-all group hover:border-purple-500/50 min-h-[200px] flex items-center justify-center"
              >
                {images.right ? (
                  <div className="text-center space-y-2">
                    <div className="text-5xl">✅</div>
                    <p className="text-sm text-gray-400 group-hover:text-white truncate max-w-[150px]">
                      {images.right.name}
                    </p>
                  </div>
                ) : (
                  <div className="text-center space-y-3">
                    <div className="text-6xl">📷</div>
                    <p className="text-gray-400 group-hover:text-white">Click to upload</p>
                  </div>
                )}
              </div>
            </div>
          </div>

          {/* Buttons */}
          <div className="flex gap-4 mt-8">
            <button
              onClick={handleClose}
              disabled={uploading}
              className="flex-1 bg-white/10 hover:bg-white/20 text-white font-semibold py-3 px-6 rounded-xl transition-all disabled:opacity-50"
            >
              Cancel
            </button>
            <button
              onClick={handleSubmit}
              disabled={uploading || !images.front || !images.left || !images.right}
              className="flex-1 bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 text-white font-bold py-3 px-6 rounded-xl disabled:opacity-50 disabled:cursor-not-allowed transition-all"
            >
              {uploading ? '🔄 Processing...' : '🚀 Analyze Body Type'}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

