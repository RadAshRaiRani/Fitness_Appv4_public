# Frontend - Next.js Application

Modern Next.js frontend with Clerk authentication for the Fitness App.

## Quick Start

1. **Install dependencies:**
   ```bash
   npm install
   ```

2. **Set up environment:**
   ```bash
   cp .env.example .env.local
   # Edit .env.local and add your Clerk keys and API URL
   ```

3. **Start development server:**
   ```bash
   npm run dev
   ```

App runs on **http://localhost:3000**

## Environment Variables

Create `.env.local` with:
- `NEXT_PUBLIC_API_URL` - Backend API URL (default: http://localhost:8000)
- `NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY` - Clerk publishable key
- `CLERK_SECRET_KEY` - Clerk secret key

Get Clerk keys from: https://clerk.com

## Project Structure

```
frontend/
├── app/
│   ├── page.tsx          # Landing page
│   ├── dashboard/        # Dashboard page
│   ├── diet/             # Diet page
│   ├── workout/          # Workout page
│   ├── results/          # Results page
│   ├── layout.tsx        # Root layout
│   └── globals.css       # Global styles
├── lib/
│   └── api.ts            # API client
└── middleware.ts         # Clerk middleware
```

## Available Commands

```bash
# Development
npm run dev

# Production build
npm run build
npm run start

# Lint
npm run lint
```

## Features

- ✅ Clerk authentication
- ✅ Responsive design
- ✅ Modern UI with Tailwind CSS
- ✅ TypeScript
- ✅ Next.js 16 App Router
