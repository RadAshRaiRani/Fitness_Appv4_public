'use client';

import { useUser, SignOutButton } from '@clerk/nextjs';
import { useState, useEffect, useRef, useCallback } from 'react';
import { useRouter, usePathname } from 'next/navigation';
import ImageUploadModal from '../components/ImageUploadModal';
import { API_ENDPOINTS } from '../lib/api';

// Helper function to initialize state from localStorage (synchronous)
function getInitialStateFromStorage(userId: string | undefined) {
  if (!userId) {
    return { hasResults: false, bodyType: null, gender: null };
  }

  try {
    const storedData = localStorage.getItem('fitness_results');
    if (storedData) {
      const parsed = JSON.parse(storedData);
      // Only use localStorage data if it belongs to the current user
      if (parsed.clerk_user_id && parsed.clerk_user_id === userId) {
        return {
          hasResults: true,
          bodyType: parsed.body_type || null,
          gender: parsed.gender || null
        };
      }
    }
  } catch (err) {
    console.error('Error parsing localStorage data:', err);
  }

  return { hasResults: false, bodyType: null, gender: null };
}

export default function DashboardPage() {
  const { user, isLoaded } = useUser();
  const router = useRouter();
  const pathname = usePathname();
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [uploading, setUploading] = useState(false);
  
  // Initialize state from localStorage immediately (synchronous)
  const initialState = getInitialStateFromStorage(user?.id);
  const [hasResults, setHasResults] = useState(initialState.hasResults);
  const [bodyTypeResult, setBodyTypeResult] = useState<string | null>(initialState.bodyType);
  const [userGender, setUserGender] = useState<string | null>(initialState.gender);
  
  const [motivationalSentence, setMotivationalSentence] = useState<string | null>(null);
  const [loadingMotivational, setLoadingMotivational] = useState(false);
  const lastPathnameRef = useRef<string | null>(null); // Track last pathname to detect navigation

  // Function to fetch user data (memoized to avoid dependency issues)
  const fetchUserData = useCallback(async () => {
    if (!isLoaded || !user?.id) return;

    try {
      const response = await fetch(
        API_ENDPOINTS.users.latestPlan(user.id)
      );
      if (response.ok) {
        const data = await response.json();
        if (data.plan) {
          console.log('✅ Found classification in database:', data.plan.body_type);
          setBodyTypeResult(data.plan.body_type);
          // Only set gender if it exists in the plan
          if (data.plan.gender) {
            setUserGender(data.plan.gender);
          }
          setHasResults(true);
          
          // Update localStorage with current user's data
          const results = {
            clerk_user_id: user.id, // Store Clerk ID to verify ownership
            body_type: data.plan.body_type,
            gender: data.plan.gender,
            workout_plan: data.plan.workout_plan || '',
            meal_plan: data.plan.meal_plan || ''
          };
          localStorage.setItem('fitness_results', JSON.stringify(results));
          return;
        } else {
          // No plan found in database - only update if we don't have localStorage data
          const storedData = localStorage.getItem('fitness_results');
          if (!storedData) {
            setHasResults(false);
            setBodyTypeResult(null);
            setUserGender(null);
          }
          // If localStorage has data, keep it (user might have generated plans but not saved to DB)
        }
      } else if (response.status === 404) {
        // User has no plan yet - only update if we don't have localStorage data
        const storedData = localStorage.getItem('fitness_results');
        if (!storedData) {
          setHasResults(false);
          setBodyTypeResult(null);
          setUserGender(null);
        }
        // If localStorage has data, keep it (user might have generated plans but not saved to DB)
      }
    } catch (err) {
      console.error('Failed to fetch from backend:', err);
      // Don't reset state on error - keep existing state from localStorage
      // This ensures if API fails, we still show the user's data from localStorage
    }
    
    // Note: We don't need to check localStorage here anymore since we initialize from it
    // The API call above will update localStorage if it has newer data
  }, [isLoaded, user?.id]);

  // Function to check if we need a new motivational sentence (daily refresh)
  const shouldFetchNewSentence = useCallback(() => {
    const lastFetchDate = localStorage.getItem('motivational_sentence_date');
    const today = new Date().toDateString();
    
    // If no stored date or it's a different day, fetch new sentence
    if (!lastFetchDate || lastFetchDate !== today) {
      return true;
    }
    
    return false;
  }, []);

  // Function to fetch motivational sentence
  const fetchMotivationalSentence = useCallback(async (forceRefresh = false) => {
    if (loadingMotivational) return;
    
    // Check if we need a new sentence (unless forced)
    if (!forceRefresh && !shouldFetchNewSentence()) {
      // Load existing sentence from localStorage if available
      const storedSentence = localStorage.getItem('motivational_sentence');
      if (storedSentence) {
        setMotivationalSentence(storedSentence);
        return;
      }
    }
    
    try {
      setLoadingMotivational(true);
      const dayOfWeek = new Date().toLocaleDateString('en-US', { weekday: 'long' });
      const tones = ['Energetic', 'Stoic', 'Scientific', 'Empathetic'];
      const randomTone = tones[Math.floor(Math.random() * tones.length)];
      
      const response = await fetch(API_ENDPOINTS.agents.motivational, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          tone: randomTone,
          day_of_week: dayOfWeek
        })
      });
      
      if (response.ok) {
        const data = await response.json();
        setMotivationalSentence(data.sentence);
        
        // Store in localStorage with today's date
        localStorage.setItem('motivational_sentence', data.sentence);
        localStorage.setItem('motivational_sentence_date', new Date().toDateString());
      }
    } catch (err) {
      console.error('Failed to fetch motivational sentence:', err);
      // Fallback to stored sentence if fetch fails
      const storedSentence = localStorage.getItem('motivational_sentence');
      if (storedSentence) {
        setMotivationalSentence(storedSentence);
      }
    } finally {
      setLoadingMotivational(false);
    }
  }, [loadingMotivational, shouldFetchNewSentence]);

  // Update state when user loads (re-initialize from localStorage for new user)
  useEffect(() => {
    if (isLoaded && user?.id) {
      // Re-check localStorage now that we have user ID (more accurate check)
      const newState = getInitialStateFromStorage(user.id);
      setHasResults(newState.hasResults);
      setBodyTypeResult(newState.bodyType);
      setUserGender(newState.gender);
      
      // Then fetch from API to verify/update (this happens in background)
      fetchUserData();
      fetchMotivationalSentence();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [user?.id, isLoaded]);

  // Refetch data when navigating back to dashboard from another page
  useEffect(() => {
    // Only refetch if we're on dashboard AND we came from another page (not initial load)
    if (pathname === '/dashboard' && isLoaded && user?.id) {
      const lastPathname = lastPathnameRef.current;
      
      // If we were on a different page before, refetch
      if (lastPathname && lastPathname !== '/dashboard') {
        console.log('🔄 Navigated back to dashboard from', lastPathname, '- refetching user data...');
        fetchUserData();
      }
      
      // Update the ref for next time
      lastPathnameRef.current = pathname;
    } else if (pathname) {
      // Update ref even if not on dashboard
      lastPathnameRef.current = pathname;
    }
  }, [pathname, isLoaded, user?.id]);

  // Also refetch when window gets focus (user clicks back button or switches tabs)
  useEffect(() => {
    const handleFocus = () => {
      if (pathname === '/dashboard' && isLoaded && user?.id) {
        console.log('🔄 Window focused on dashboard - refetching user data...');
        fetchUserData();
        // Check if we need a new motivational sentence (daily refresh)
        fetchMotivationalSentence();
      }
    };

    window.addEventListener('focus', handleFocus);
    return () => {
      window.removeEventListener('focus', handleFocus);
    };
  }, [pathname, isLoaded, user?.id, fetchMotivationalSentence]);

  // Check for daily refresh when page becomes visible (handles overnight scenarios)
  useEffect(() => {
    const handleVisibilityChange = () => {
      if (document.visibilityState === 'visible' && pathname === '/dashboard' && isLoaded && user?.id) {
        // Check if it's a new day and fetch new sentence if needed
        if (shouldFetchNewSentence()) {
          console.log('📅 New day detected - fetching new motivational sentence...');
          fetchMotivationalSentence(true);
        }
      }
    };

    document.addEventListener('visibilitychange', handleVisibilityChange);
    return () => {
      document.removeEventListener('visibilitychange', handleVisibilityChange);
    };
  }, [pathname, isLoaded, user?.id, shouldFetchNewSentence, fetchMotivationalSentence]);

  // Note: Gender is only set when images are uploaded and classification is done
  // It's handled in the first useEffect when fetching user data

  // Derived values (not hooks, so can be after hooks)
  // Only show gender if it has been detected (user has uploaded images)
  const hasGender = userGender !== null;
  const genderEmoji = hasGender ? (userGender === 'female' ? '👩' : '👨') : '👤';
  const isNewUser = !hasResults; // New user if no classification results exist

  if (!isLoaded) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-purple-900 via-gray-900 to-pink-900 flex items-center justify-center">
        <div className="text-white text-xl">Loading...</div>
      </div>
    );
  }

  const handleModalSubmit = async (images: { front: File | null; left: File | null; right: File | null }) => {
    setUploading(true);
    setIsModalOpen(false);

    try {
      // Validate images
      if (!images.front || !images.left || !images.right) {
        alert('Please upload all three images');
        setUploading(false);
        return;
      }

      const formData = new FormData();
      formData.append('front_image', images.front);
      formData.append('left_image', images.left);
      formData.append('right_image', images.right);

      const apiUrl = API_ENDPOINTS.classify.bodyType;
      console.log('📤 Uploading images to:', apiUrl);
      console.log('📤 API URL from env:', process.env.NEXT_PUBLIC_API_URL);

      const response = await fetch(apiUrl, {
        method: 'POST',
        body: formData,
        // Don't set Content-Type header - browser will set it with boundary for FormData
      });

      console.log('📥 Response status:', response.status);

      if (!response.ok) {
        const errorText = await response.text();
        console.error('❌ Classification failed:', errorText);
        throw new Error(`Classification failed: ${response.status} ${response.statusText}`);
      }

      const data = await response.json();
      
      // Use detected gender from API response (should always be present after classification)
      const detectedGender = data.gender || 'male'; // API should always return gender
      
      // Update state immediately
      setUserGender(detectedGender);
      setBodyTypeResult(data.body_type);
      setHasResults(true);
      
      // Save to database via backend API
      try {
        await fetch(API_ENDPOINTS.users.classify, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            clerk_user_id: user?.id || '',
            body_type: data.body_type,
            gender: detectedGender,
            workout_plan: data.workout_plan || '',
            meal_plan: data.meal_plan || ''
          })
        });
      } catch (err) {
        console.error('Failed to save to database:', err);
      }
      
      // Also store in localStorage as fallback (with Clerk ID to verify ownership)
      const results = {
        clerk_user_id: user?.id || '', // Store Clerk ID to verify ownership
        body_type: data.body_type,
        gender: detectedGender,
        workout_plan: data.workout_plan || '',
        meal_plan: data.meal_plan || ''
      };
      localStorage.setItem('fitness_results', JSON.stringify(results));
      
      router.push('/results');
    } catch (error) {
      console.error('❌ Error in handleModalSubmit:', error);
      const errorMessage = error instanceof Error ? error.message : 'Unknown error';
      alert(`Failed to classify body type: ${errorMessage}\n\nPlease check:\n1. Backend server is running (http://localhost:8000)\n2. All three images are uploaded\n3. Try again`);
    } finally {
      setUploading(false);
    }
  };

  return (
    <>
      <div className="min-h-screen bg-gradient-to-br from-purple-900 via-gray-900 to-pink-900">
        {/* Header */}
        <div className="bg-black/20 backdrop-blur-xl border-b border-white/10">
              <div className="max-w-7xl mx-auto px-4 py-6">
                <div className="flex justify-between items-center mb-3">
                  <h1 className="text-3xl font-bold bg-gradient-to-r from-purple-400 via-pink-400 to-purple-600 bg-clip-text text-transparent">
                    Agentic Fit Dashboard
                  </h1>
                  <div className="flex gap-3 items-center">
                  <button
                    onClick={() => router.push('/admin')}
                    className="bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 text-white px-4 py-2 rounded-lg shadow-lg transition-all duration-300"
                  >
                    🔐 Admin
                  </button>
                  <SignOutButton>
                    <button 
                      onClick={() => {
                        // Clear localStorage on sign out
                        localStorage.removeItem('fitness_results');
                        localStorage.removeItem('workoutPlan');
                        localStorage.removeItem('mealPlan');
                      }}
                      className="bg-red-500/20 hover:bg-red-500/30 text-red-400 px-4 py-2 rounded-lg border border-red-500/30 transition-all"
                    >
                      Sign Out
                    </button>
                  </SignOutButton>
                  </div>
                </div>
                {/* Motivational Sentence */}
                {motivationalSentence && (
                  <div className="max-w-7xl mx-auto px-4">
                    <div className="bg-gradient-to-r from-purple-500/20 via-pink-500/20 to-purple-500/20 backdrop-blur-sm rounded-xl p-4 border border-white/10">
                      <p className="text-white text-lg font-semibold text-center italic">
                        "{motivationalSentence}"
                      </p>
                    </div>
                  </div>
                )}
                {loadingMotivational && !motivationalSentence && (
                  <div className="max-w-7xl mx-auto px-4 mt-3">
                    <div className="bg-white/5 backdrop-blur-sm rounded-xl p-4 border border-white/10">
                      <p className="text-gray-400 text-center">Loading your motivation...</p>
                    </div>
                  </div>
                )}
              </div>
        </div>

        <div className="max-w-7xl mx-auto px-4 py-8 pb-12">
          {/* User Info Card */}
          <div className="bg-white/10 backdrop-blur-xl rounded-3xl p-8 mb-12 shadow-2xl border border-white/20">
            <div className="flex items-center gap-6 mb-6">
              <div className="w-24 h-24 bg-gradient-to-br from-purple-500 to-pink-500 rounded-full flex items-center justify-center text-5xl">
                {genderEmoji}
              </div>
              <div>
                <h2 className="text-3xl font-bold text-white mb-2">
                  {isNewUser ? 'Hi' : 'Welcome back'}, {user?.firstName || 'User'}!
                </h2>
                <p className="text-gray-300">
                  {user?.emailAddresses?.[0]?.emailAddress}
                </p>
                {hasGender && (
                  <p className="text-sm text-gray-400 capitalize mt-1">
                    {userGender === 'female' ? '👩 Female' : '👨 Male'}
                  </p>
                )}
              </div>
            </div>
          </div>

          {/* Body Type Classification Card - Only show upload if no results */}
          {!hasResults && (
            <div className="bg-white/10 backdrop-blur-xl rounded-3xl p-8 pb-12 shadow-2xl border border-white/20 mb-12">
              <h3 className="text-2xl font-bold text-white mb-6 text-center">
                🎯 Body Type Classification
              </h3>
              <p className="text-gray-300 text-center mb-8">
                Get personalized workout and meal plans based on your body type
              </p>

              {/* Main Upload Button */}
              <div className="flex justify-center py-8">
                <button
                  onClick={() => setIsModalOpen(true)}
                  disabled={uploading}
                  className="bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 text-white font-bold py-6 px-12 rounded-2xl text-xl disabled:opacity-50 disabled:cursor-not-allowed transition-all shadow-lg hover:shadow-2xl flex items-center gap-3"
                >
                  {uploading ? (
                    <>
                      <span className="animate-spin">🔄</span>
                      Processing...
                    </>
                  ) : (
                    <>
                      📸 Upload Body Images
                    </>
                  )}
                </button>
              </div>
            </div>
          )}

          {/* Results Display (if classification already done) */}
          {hasResults && bodyTypeResult && (
            <div className="bg-gradient-to-br from-purple-600/20 to-pink-600/20 backdrop-blur-xl rounded-3xl p-8 pb-10 mb-12 shadow-2xl border border-purple-500/30">
              <h3 className="text-2xl font-bold text-white mb-6 text-center">
                ✅ Your Classification Results
              </h3>
              
              <div className="text-center mb-6">
                <div className="text-8xl mb-4">
                  {userGender === 'female' ? '👩' : '👨'}
                </div>
                <h4 className="text-3xl font-bold text-white mb-2 capitalize">
                  {bodyTypeResult}
                </h4>
                <p className="text-gray-300 mb-2">
                  Your personalized plans are ready!
                </p>
                {userGender && (
                  <p className="text-sm text-gray-400 capitalize">
                    {userGender === 'female' ? '👩 Female' : '👨 Male'}
                  </p>
                )}
              </div>

              <div className="grid md:grid-cols-2 gap-6 mt-8">
                <button
                  onClick={() => router.push('/workout')}
                  className="bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 text-white font-bold py-4 px-6 rounded-xl transition-all shadow-lg hover:shadow-2xl flex items-center justify-center gap-3"
                >
                  💪 View Workout Plan
                </button>
                <button
                  onClick={() => router.push('/diet')}
                  className="bg-gradient-to-r from-pink-600 to-purple-600 hover:from-pink-700 hover:to-purple-700 text-white font-bold py-4 px-6 rounded-xl transition-all shadow-lg hover:shadow-2xl flex items-center justify-center gap-3"
                >
                  🍎 View Meal Plan
                </button>
              </div>

              <div className="mt-8 mb-8">
                <button
                  onClick={() => router.push('/results')}
                  className="w-full bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 text-white font-bold py-4 px-6 rounded-xl transition-all shadow-lg hover:shadow-2xl flex items-center justify-center gap-3"
                >
                  📊 View Full Results
                </button>
              </div>

              <div className="mt-4 text-center">
                <button
                  onClick={() => {
                    setIsModalOpen(true);
                  }}
                  className="text-gray-400 hover:text-white text-sm underline transition-all"
                >
                  🔄 Re-upload Images
                </button>
              </div>
            </div>
          )}

          {/* Features Grid */}
          <div className="grid md:grid-cols-3 gap-6">
            <div className="bg-white/5 backdrop-blur-sm rounded-2xl p-6 border border-white/10 hover:bg-white/10 transition-all">
              <div className="text-4xl mb-3">💪</div>
              <h4 className="text-lg font-bold text-white mb-2">Workout Plans</h4>
              <p className="text-gray-400 text-sm">AI-generated 4-week personalized workout plans</p>
            </div>
            <div className="bg-white/5 backdrop-blur-sm rounded-2xl p-6 border border-white/10 hover:bg-white/10 transition-all">
              <div className="text-4xl mb-3">🍎</div>
              <h4 className="text-lg font-bold text-white mb-2">Diet Plans</h4>
              <p className="text-gray-400 text-sm">Customized nutrition plans for your body type</p>
            </div>
            <div className="bg-white/5 backdrop-blur-sm rounded-2xl p-6 border border-white/10 hover:bg-white/10 transition-all">
              <div className="text-4xl mb-3">📊</div>
              <h4 className="text-lg font-bold text-white mb-2">Track Progress</h4>
              <p className="text-gray-400 text-sm">Monitor your fitness journey</p>
            </div>
          </div>
        </div>
      </div>

      {/* Image Upload Modal */}
      <ImageUploadModal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        onSubmit={handleModalSubmit}
      />
    </>
  );
}
