'use client';

import { useUser } from '@clerk/nextjs';
import { useRouter, usePathname } from 'next/navigation';
import { SignOutButton } from '@clerk/nextjs';

export default function TopNav() {
  const { user, isLoaded } = useUser();
  const router = useRouter();
  const pathname = usePathname();

  // Don't show nav on login page or pages with their own headers
  if (pathname === '/' || pathname === '/dashboard' || pathname === '/admin') {
    return null;
  }

  return (
    <nav className="bg-black/20 backdrop-blur-xl border-b border-white/10 sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 py-4">
        <div className="flex justify-between items-center">
          {/* Logo/Title */}
          <div 
            onClick={() => router.push('/dashboard')}
            className="cursor-pointer"
          >
            <h1 className="text-2xl font-bold bg-gradient-to-r from-purple-400 via-pink-400 to-purple-600 bg-clip-text text-transparent">
              Agentic Fit
            </h1>
          </div>

          {/* Navigation Links */}
          <div className="flex items-center gap-4">
            {isLoaded && user && (
              <>
                <button
                  onClick={() => router.push('/dashboard')}
                  className={`px-4 py-2 rounded-lg transition-all ${
                    pathname === '/dashboard'
                      ? 'bg-purple-500/30 text-white'
                      : 'text-gray-300 hover:text-white hover:bg-white/10'
                  }`}
                >
                  Dashboard
                </button>
                <button
                  onClick={() => router.push('/admin')}
                  className={`px-4 py-2 rounded-lg transition-all flex items-center gap-2 ${
                    pathname === '/admin'
                      ? 'bg-gradient-to-r from-purple-600 to-pink-600 text-white shadow-lg'
                      : 'bg-gradient-to-r from-purple-600/80 to-pink-600/80 hover:from-purple-600 hover:to-pink-600 text-white border border-purple-500/30'
                  }`}
                >
                  🔐 Admin
                </button>
                <SignOutButton>
                  <button className="bg-red-500/20 hover:bg-red-500/30 text-red-400 px-4 py-2 rounded-lg border border-red-500/30 transition-all">
                    Sign Out
                  </button>
                </SignOutButton>
              </>
            )}
            {isLoaded && !user && (
              <button
                onClick={() => router.push('/')}
                className="px-4 py-2 rounded-lg text-gray-300 hover:text-white hover:bg-white/10 transition-all"
              >
                Sign In
              </button>
            )}
          </div>
        </div>
      </div>
    </nav>
  );
}

