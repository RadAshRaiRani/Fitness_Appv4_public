'use client';

import { SignIn, SignUp, useUser } from '@clerk/nextjs';
import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';

export default function Home() {
  const { isSignedIn, isLoaded } = useUser();
  const router = useRouter();
  const [isSignIn, setIsSignIn] = useState(true);

  useEffect(() => {
    if (isLoaded && isSignedIn) {
      // Immediately redirect to dashboard if user is signed in
      router.replace('/dashboard');
    }
  }, [isLoaded, isSignedIn, router]);

  // Show loading state while checking authentication
  if (!isLoaded) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-purple-900 via-gray-900 to-pink-900 flex items-center justify-center">
        <div className="text-white text-xl">Loading...</div>
      </div>
    );
  }

  // Don't render auth UI if user is already signed in (redirect will happen)
  if (isSignedIn) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-purple-900 via-gray-900 to-pink-900 flex items-center justify-center">
        <div className="text-white text-xl">Redirecting to dashboard...</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-900 via-gray-900 to-pink-900 flex flex-col">
      {/* Top Navigation Bar */}
      <div className="bg-black/20 backdrop-blur-xl border-b border-white/10 w-full">
        <div className="max-w-7xl mx-auto px-4 py-4 flex justify-end">
          <button
            onClick={() => router.push('/admin')}
            className="px-6 py-2 rounded-lg font-semibold transition-all duration-300 bg-gradient-to-r from-purple-600 to-pink-600 text-white shadow-lg hover:from-purple-700 hover:to-pink-700 flex items-center justify-center gap-2"
            title="Sign in as Admin"
          >
            🔐 Sign in as Admin
          </button>
        </div>
      </div>

      {/* Main Content */}
      <div className="flex-1 flex items-center justify-center p-4">
        {/* Background decorations */}
        <div className="absolute inset-0 overflow-hidden pointer-events-none">
          <div className="absolute top-0 left-1/4 w-72 h-72 bg-purple-500 opacity-20 rounded-full blur-3xl"></div>
          <div className="absolute bottom-0 right-1/4 w-96 h-96 bg-pink-500 opacity-20 rounded-full blur-3xl"></div>
          <div className="absolute top-1/2 left-0 w-96 h-96 bg-gray-500 opacity-20 rounded-full blur-3xl"></div>
        </div>

      <div className="relative z-10 w-full max-w-md">
        {/* Logo and Title */}
        <div className="text-center mb-8">
          <h1 className="text-6xl md:text-7xl font-bold bg-gradient-to-r from-purple-400 via-pink-400 to-purple-600 bg-clip-text text-transparent mb-4">
            Agentic Fit
          </h1>
          <p className="text-xl text-gray-300 font-light">
            AI-Powered Personal Training
          </p>
          <p className="text-sm text-gray-400 mt-2">
            Get personalized workout and diet plans powered by AI
          </p>
        </div>

                  {/* Auth Container */}
        <div className="bg-white/10 backdrop-blur-xl rounded-3xl p-8 shadow-2xl border border-white/20 mb-12">
          {/* Toggle Buttons */}
          <div className="flex gap-2 mb-6 p-1 bg-black/20 rounded-xl">
            <button
              onClick={() => setIsSignIn(true)}
              className={`flex-1 py-3 px-4 rounded-lg font-semibold transition-all duration-300 ${
                isSignIn
                  ? 'bg-gradient-to-r from-purple-600 to-pink-600 text-white shadow-lg'
                  : 'text-gray-300 hover:text-white'
              }`}
            >
              Sign In
            </button>
            <button
              onClick={() => setIsSignIn(false)}
              className={`flex-1 py-3 px-4 rounded-lg font-semibold transition-all duration-300 ${
                !isSignIn
                  ? 'bg-gradient-to-r from-purple-600 to-pink-600 text-white shadow-lg'
                  : 'text-gray-300 hover:text-white'
              }`}
            >
              Join Now
            </button>
            <button
              onClick={() => router.push('/admin')}
              className="px-4 py-3 rounded-lg font-semibold transition-all duration-300 bg-gradient-to-r from-purple-600 to-pink-600 text-white shadow-lg hover:from-purple-700 hover:to-pink-700 flex items-center justify-center gap-2"
              title="Sign in as Admin"
            >
              🔐 Admin
            </button>
          </div>

          {/* Clerk Auth Components */}
          <div className="min-h-[500px]">
            {isSignIn ? (
              <div className="flex flex-col items-center">
                <SignIn 
                  routing="hash"
                  redirectUrl="/dashboard"
                  appearance={{
                    elements: {
                      rootBox: "w-full mx-auto",
                      card: "bg-transparent shadow-none w-full",
                      headerTitle: "text-white text-2xl font-bold text-center",
                      headerSubtitle: "text-gray-400 text-center",
                      socialButtonsBlockButton: "bg-white/10 hover:bg-white/20 text-white border-white/20 w-full justify-center",
                      formButtonPrimary: "bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 text-white w-full justify-center",
                      formFieldInput: "bg-white/10 border-white/20 text-white placeholder-gray-400 w-full",
                      formFieldLabel: "text-gray-300",
                      footerActionLink: "text-purple-400 hover:text-pink-400",
                      identityPreviewText: "text-white",
                      identityPreviewEditButton: "text-purple-400 hover:text-pink-400",
                      form: "w-full flex flex-col items-center",
                    },
                    layout: {
                      socialButtonsPlacement: "top"
                    }
                  }}
                />
              </div>
            ) : (
              <div className="flex flex-col items-center">
                <SignUp
                  routing="hash"
                  redirectUrl="/dashboard"
                  appearance={{
                    elements: {
                      rootBox: "w-full mx-auto",
                      card: "bg-transparent shadow-none w-full",
                      headerTitle: "text-white text-2xl font-bold text-center",
                      headerSubtitle: "text-gray-400 text-center",
                      socialButtonsBlockButton: "bg-white/10 hover:bg-white/20 text-white border-white/20 w-full justify-center",
                      formButtonPrimary: "bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 text-white w-full justify-center",
                      formFieldInput: "bg-white/10 border-white/20 text-white placeholder-gray-400 w-full",
                      formFieldLabel: "text-gray-300",
                      footerActionLink: "text-purple-400 hover:text-pink-400",
                      identityPreviewText: "text-white",
                      identityPreviewEditButton: "text-purple-400 hover:text-pink-400",
                      formResendCodeLink: "text-purple-400 hover:text-pink-400",
                      form: "w-full flex flex-col items-center",
                    },
                    layout: {
                      socialButtonsPlacement: "top"
                    }
                  }}
                />
              </div>
            )}
          </div>
        </div>

        {/* Features */}
        <div className="mt-16 text-center">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm text-gray-300">
            <div className="bg-white/5 backdrop-blur-sm rounded-lg p-4">
              <div className="text-2xl mb-2">💪</div>
              <div className="font-semibold text-white">Personalized Plans</div>
              <div className="text-gray-400 text-xs">AI-optimized workouts</div>
            </div>
            <div className="bg-white/5 backdrop-blur-sm rounded-lg p-4">
              <div className="text-2xl mb-2">🍎</div>
              <div className="font-semibold text-white">Smart Nutrition</div>
              <div className="text-gray-400 text-xs">Custom meal plans</div>
            </div>
            <div className="bg-white/5 backdrop-blur-sm rounded-lg p-4">
              <div className="text-2xl mb-2">📊</div>
              <div className="font-semibold text-white">Track Progress</div>
              <div className="text-gray-400 text-xs">Monitor your goals</div>
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="mt-8 text-center text-gray-400 text-xs">
          Powered by AI • Built with Next.js & Clerk
        </div>
      </div>
      </div>
    </div>
  );
}
