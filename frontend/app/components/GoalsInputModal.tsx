'use client';

import { useState } from 'react';

interface GoalsInputModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (goals: string) => void;
  bodyType?: string;
}

export default function GoalsInputModal({ isOpen, onClose, onSubmit, bodyType }: GoalsInputModalProps) {
  const [goals, setGoals] = useState('');
  const [selectedPreset, setSelectedPreset] = useState<string>('');

  const presetGoals = [
    { label: 'Weight Loss', value: 'weight loss and fat reduction' },
    { label: 'Muscle Gain', value: 'muscle building and strength gain' },
    { label: 'General Fitness', value: 'overall fitness and health improvement' },
    { label: 'Athletic Performance', value: 'athletic performance and endurance' },
    { label: 'Body Recomposition', value: 'body recomposition - lose fat and gain muscle' },
    { label: 'Strength Building', value: 'strength building and power development' },
    { label: 'Flexibility & Mobility', value: 'flexibility, mobility, and injury prevention' },
    { label: 'Custom', value: '' }
  ];

  const handlePresetSelect = (preset: string) => {
    setSelectedPreset(preset);
    if (preset) {
      setGoals(preset);
    } else {
      setGoals('');
    }
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (goals.trim()) {
      onSubmit(goals.trim());
      setGoals('');
      setSelectedPreset('');
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black/70 backdrop-blur-sm z-50 flex items-center justify-center p-4">
      <div className="bg-gradient-to-br from-purple-900 via-gray-900 to-pink-900 rounded-3xl p-8 max-w-2xl w-full border border-white/20 shadow-2xl">
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-3xl font-bold bg-gradient-to-r from-purple-400 to-pink-400 bg-clip-text text-transparent">
            What are your fitness goals?
          </h2>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-white text-2xl transition-colors"
          >
            ×
          </button>
        </div>

        {bodyType && (
          <p className="text-gray-300 mb-6">
            Based on your body type (<span className="font-semibold capitalize">{bodyType}</span>), 
            we'll create a personalized plan tailored to your goals.
          </p>
        )}

        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Preset Goals */}
          <div>
            <label className="block text-white font-semibold mb-3">
              Choose a goal or create your own:
            </label>
            <div className="grid grid-cols-2 gap-3 mb-4">
              {presetGoals.map((preset) => (
                <button
                  key={preset.label}
                  type="button"
                  onClick={() => handlePresetSelect(preset.value)}
                  className={`p-4 rounded-xl border-2 transition-all ${
                    selectedPreset === preset.value
                      ? 'border-purple-500 bg-purple-500/20 text-white'
                      : 'border-white/20 bg-white/5 text-gray-300 hover:border-purple-400 hover:bg-white/10'
                  }`}
                >
                  {preset.label}
                </button>
              ))}
            </div>
          </div>

          {/* Custom Goals Input */}
          <div>
            <label htmlFor="goals" className="block text-white font-semibold mb-2">
              Your Fitness Goals:
            </label>
            <textarea
              id="goals"
              value={goals}
              onChange={(e) => {
                setGoals(e.target.value);
                if (e.target.value) {
                  setSelectedPreset('');
                }
              }}
              placeholder="E.g., I want to lose 20 pounds in 3 months while building muscle..."
              className="w-full bg-white/10 border border-white/20 rounded-xl p-4 text-white placeholder-gray-400 focus:outline-none focus:border-purple-500 focus:ring-2 focus:ring-purple-500/50 min-h-[120px] resize-none"
              required
            />
            <p className="text-gray-400 text-sm mt-2">
              Be specific about what you want to achieve. This helps us create a better plan for you.
            </p>
          </div>

          {/* Submit Button */}
          <div className="flex gap-4">
            <button
              type="button"
              onClick={onClose}
              className="flex-1 px-6 py-3 bg-white/10 hover:bg-white/20 border border-white/20 rounded-xl font-semibold text-white transition-all"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={!goals.trim()}
              className="flex-1 px-6 py-3 bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 disabled:opacity-50 disabled:cursor-not-allowed rounded-xl font-semibold text-white transition-all shadow-lg"
            >
              Save Goals & Continue
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

