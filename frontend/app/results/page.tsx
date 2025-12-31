'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { useUser } from '@clerk/nextjs';

interface ResultsPageProps {
  bodyType?: string;
  gender?: string;
  recommendations?: any;
}

export default function ResultsPage({ bodyType, gender, recommendations }: ResultsPageProps) {
  const router = useRouter();
  const { user } = useUser();
  const [bodyTypeData, setBodyTypeData] = useState(bodyType);
  const [genderData, setGenderData] = useState(gender);
  const [workoutPlan, setWorkoutPlan] = useState<string>('');
  const [mealPlan, setMealPlan] = useState<string>('');

  useEffect(() => {
    if (!bodyTypeData) {
      const data = localStorage.getItem('fitness_results');
      if (data) {
        try {
          const parsed = JSON.parse(data);
          // Verify the data belongs to current user
          if (parsed.clerk_user_id && user?.id && parsed.clerk_user_id === user.id) {
            // Data belongs to current user
            setBodyTypeData(parsed.body_type);
            setGenderData(parsed.gender);
            setWorkoutPlan(parsed.workout_plan || '');
            setMealPlan(parsed.meal_plan || '');
          } else {
            // Data doesn't belong to current user or old format - clear it
            console.log('🧹 Clearing localStorage data (different user or old format)');
            localStorage.removeItem('fitness_results');
            localStorage.removeItem('workoutPlan');
            localStorage.removeItem('mealPlan');
          }
        } catch (err) {
          console.error('Error parsing localStorage data:', err);
          localStorage.removeItem('fitness_results');
          localStorage.removeItem('workoutPlan');
          localStorage.removeItem('mealPlan');
        }
      }
    }
  }, [bodyTypeData, user?.id]);

  // Get avatar based on body type and gender
  const getAvatar = (type: string, gen: string) => {
    const isFemale = gen === 'female';
    
    const avatars: Record<string, string> = {
      ectomorph: isFemale ? '👱‍♀️' : '👱‍♂️',
      mesomorph: isFemale ? '💪🏻' : '💪',
      endomorph: isFemale ? '👩‍🦱' : '👨‍🦱',
    };
    
    return avatars[type.toLowerCase()] || '👤';
  };

  // Get body type info
  const getBodyTypeInfo = (type: string) => {
    const types: Record<string, { name: string; description: string; characteristics: string[] }> = {
      ectomorph: {
        name: 'Ectomorph',
        description: 'Naturally thin and lean with a fast metabolism',
        characteristics: ['Fast metabolism', 'Naturally lean', 'Difficulty gaining weight', 'High energy']
      },
      mesomorph: {
        name: 'Mesomorph',
        description: 'Athletic build with natural muscle definition',
        characteristics: ['Gains muscle easily', 'Athletic build', 'Balanced metabolism', 'Strong']
      },
      endomorph: {
        name: 'Endomorph',
        description: 'Naturally curvy with a slower metabolism',
        characteristics: ['Slower metabolism', 'Gains weight easily', 'Natural strength', 'Rounder physique']
      }
    };
    
    return types[type.toLowerCase()] || { name: type, description: 'Unknown', characteristics: [] };
  };

  const handleBackToDashboard = () => {
    router.push('/dashboard');
  };

  const info = bodyTypeData ? getBodyTypeInfo(bodyTypeData) : null;

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-900 via-gray-900 to-pink-900">
      {/* Header */}
      <div className="bg-black/20 backdrop-blur-xl border-b border-white/10">
        <div className="max-w-7xl mx-auto px-4 py-6 flex justify-between items-center">
          <h1 className="text-3xl font-bold bg-gradient-to-r from-purple-400 via-pink-400 to-purple-600 bg-clip-text text-transparent">
            Your Results
          </h1>
          <button
            onClick={handleBackToDashboard}
            className="px-6 py-3 bg-white/10 hover:bg-white/20 backdrop-blur-lg rounded-full font-semibold transition-all duration-300 hover:scale-105 text-white"
          >
            ← Back to Dashboard
          </button>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 py-8">
        {!bodyTypeData ? (
          <div className="bg-white/10 backdrop-blur-xl rounded-3xl p-8 text-center">
            <p className="text-gray-300">No results found. Please analyze your body type first.</p>
          </div>
        ) : (
          <>
            {/* Body Type Card */}
            <div className="bg-white/10 backdrop-blur-xl rounded-3xl p-8 mb-8 shadow-2xl border border-white/20">
              <div className="text-center">
                <div className="text-9xl mb-6">{getAvatar(bodyTypeData, genderData || 'male')}</div>
                <h2 className="text-4xl font-bold text-white mb-2">
                  {info?.name || bodyTypeData}
                </h2>
                <p className="text-lg text-gray-300 mb-4 capitalize">
                  {genderData === 'female' ? '👩 Female' : '👨 Male'}
                </p>
                <p className="text-xl text-gray-300 mb-6">{info?.description}</p>
                
                {/* Characteristics */}
                <div className="grid md:grid-cols-2 gap-4 mt-8">
                  {info?.characteristics.map((char, idx) => (
                    <div key={idx} className="bg-white/5 rounded-xl p-4 border border-white/10">
                      <p className="text-gray-300">✨ {char}</p>
                    </div>
                  ))}
                </div>
              </div>
            </div>

            {/* Workout Plan */}
            <div className="bg-white/10 backdrop-blur-xl rounded-3xl p-8 mb-8 shadow-2xl border border-white/20">
              <h3 className="text-2xl font-bold text-white mb-6 flex items-center gap-3">
                <span className="text-4xl">💪</span>
                Your 4-Week Workout Plan
              </h3>
              <div className="bg-white/5 rounded-2xl p-6 border border-white/10 text-center">
                <p className="text-gray-300 mb-6">
                  {workoutPlan ? 'View your complete 4-week workout plan' : 'Your personalized workout plan will be generated here soon!'}
                </p>
                <button
                  onClick={() => router.push('/workout')}
                  className="bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 text-white font-bold py-3 px-8 rounded-xl transition-all shadow-lg hover:shadow-2xl"
                >
                  View Full Workout Plan →
                </button>
              </div>
            </div>

            {/* Meal Plan */}
            <div className="bg-white/10 backdrop-blur-xl rounded-3xl p-8 shadow-2xl border border-white/20">
              <h3 className="text-2xl font-bold text-white mb-6 flex items-center gap-3">
                <span className="text-4xl">🍎</span>
                Your 4-Week Meal Plan
              </h3>
              <div className="bg-white/5 rounded-2xl p-6 border border-white/10 text-center">
                <p className="text-gray-300 mb-6">
                  {mealPlan ? 'View your complete 4-week meal plan' : 'Your personalized meal plan will be generated here soon!'}
                </p>
                <button
                  onClick={() => router.push('/diet')}
                  className="bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 text-white font-bold py-3 px-8 rounded-xl transition-all shadow-lg hover:shadow-2xl"
                >
                  View Full Meal Plan →
                </button>
              </div>
            </div>
          </>
        )}
      </div>
    </div>
  );
}

