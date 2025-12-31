"use client";

import { useEffect, useState, useCallback } from "react";
import { useRouter } from "next/navigation";
import { useUser } from "@clerk/nextjs";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { API_ENDPOINTS } from "../lib/api";
import GoalsInputModal from "../components/GoalsInputModal";

export default function DietPage() {
  const { user } = useUser();
  const router = useRouter();
  const [plan, setPlan] = useState<string>("");
  const [status, setStatus] = useState<string>("Loading...");
  const [isGenerating, setIsGenerating] = useState(true);
  const [showGoalsModal, setShowGoalsModal] = useState(false);
  const [bodyType, setBodyType] = useState<string>("");

  const loadMealPlan = useCallback(async () => {
    // FIRST: Check if goals exist - new users must set goals before viewing/generating plans
    const storedGoals = localStorage.getItem("userGoals");
    if (!storedGoals) {
      console.log("ℹ️ No goals found - showing goals modal for new user");
      // Show goals modal if no goals are set
      setShowGoalsModal(true);
      setIsGenerating(false);
      return;
    }

    // SECOND: Try to get existing plan from localStorage (fastest)
    const storedPlan = localStorage.getItem("mealPlan");
    if (storedPlan) {
      console.log("✅ Found meal plan in localStorage");
      setPlan(storedPlan);
      setStatus("Meal Plan");
      setIsGenerating(false);
      return;
    }

    // THIRD: Check database (if user is available)
    if (user?.id) {
      try {
        console.log("🔍 Checking database for meal plan...");
        setStatus("Loading meal plan...");
        setIsGenerating(true);
        
        const response = await fetch(
          API_ENDPOINTS.users.latestPlan(user.id)
        );
        
        if (response.ok) {
          const data = await response.json();
          if (data.plan?.meal_plan) {
            console.log("✅ Found meal plan in database");
            const mealPlan = data.plan.meal_plan;
            setPlan(mealPlan);
            setStatus("Meal Plan");
            setIsGenerating(false);
            
            // Save to localStorage for faster access next time
            localStorage.setItem("mealPlan", mealPlan);
            return;
          }
        } else if (response.status === 404) {
          console.log("ℹ️ No meal plan found in database");
        }
      } catch (error) {
        console.error("❌ Error fetching meal plan from database:", error);
        // Continue to generate plan
      }
    }

    // FOURTH: If no plan found anywhere, generate new plan (goals already exist at this point)
    console.log("🚀 No plan found - generating new meal plan with existing goals");
    generateMealPlan();
  }, [user?.id]);

  useEffect(() => {
    // Get body type from localStorage
    const storedData = localStorage.getItem("classificationData");
    const fitnessResults = localStorage.getItem("fitness_results");
    
    if (fitnessResults) {
      try {
        const parsed = JSON.parse(fitnessResults);
        setBodyType(parsed.body_type || "");
      } catch (e) {
        console.error("Error parsing fitness_results:", e);
      }
    }
    
    if (storedData) {
      try {
        const data = JSON.parse(storedData);
        setBodyType(data.body_type || "");
      } catch (e) {
        console.error("Error parsing classificationData:", e);
      }
    }

    // Load meal plan: check localStorage first, then database
    loadMealPlan();
  }, [loadMealPlan]);

  const handleGoalsSubmit = (goals: string) => {
    // Store goals in localStorage
    localStorage.setItem("userGoals", goals);
    setShowGoalsModal(false);
    setIsGenerating(true);
    // Generate plan with the provided goals
    generateMealPlan(goals);
  };

  const generateMealPlan = async (customGoals?: string) => {
    try {
      console.log("🚀 Starting meal plan generation...");
      setStatus("Generating your personalized meal plan...");
      setIsGenerating(true);
      
      // Get user's body type from localStorage or use default
      const storedData = localStorage.getItem("classificationData");
      const fitnessResults = localStorage.getItem("fitness_results");
      let bodyTypeValue = "endomorph";
      
      if (fitnessResults) {
        try {
          const parsed = JSON.parse(fitnessResults);
          bodyTypeValue = parsed.body_type?.toLowerCase() || "endomorph";
        } catch (e) {
          console.error("Error parsing fitness_results:", e);
        }
      }
      
      if (storedData) {
        try {
          const data = JSON.parse(storedData);
          bodyTypeValue = data.body_type?.toLowerCase() || bodyTypeValue;
        } catch (e) {
          console.error("Error parsing classificationData:", e);
        }
      }
      
      console.log("📋 Body type:", bodyTypeValue);
      
      // Get goals from parameter, localStorage, or use default
      const goals = customGoals || localStorage.getItem("userGoals") || "balanced nutrition and health";
      console.log("🎯 Goals:", goals);
      
      // Call streaming endpoint
      const response = await fetch(API_ENDPOINTS.agents.streamRecommendations, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          body_type: bodyTypeValue,
          goals: goals,
          max_iterations: 1,
        }),
      });

      console.log("✅ Response status:", response.status);

      if (!response.ok) {
        throw new Error("Failed to generate meal plan");
      }

      const reader = response.body?.getReader();
      const decoder = new TextDecoder();

      if (!reader) {
        throw new Error("No reader available");
      }

      let mealContent = "";
      let buffer = "";

      while (true) {
        const { done, value } = await reader.read();
        
        if (done) {
          console.log("🏁 Stream complete");
          break;
        }

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split("\n\n");
        
        // Keep last incomplete line in buffer
        buffer = lines.pop() || "";

        for (const line of lines) {
          if (line.startsWith("data: ")) {
            try {
              const data = JSON.parse(line.slice(6));
              console.log("📦 Received event:", data.event);
              
              if (data.event === "status") {
                console.log("ℹ️ Status:", data.message);
                setStatus(data.message);
              } else if (data.event === "diet_complete") {
                console.log("✅ Meal plan received");
                mealContent = data.content;
                setPlan(data.content);
                setStatus("Meal Plan Generated");
                setIsGenerating(false);
                
                // Save to localStorage
                localStorage.setItem("mealPlan", data.content);
              } else if (data.event === "workout_complete") {
                // Ignore workout events on diet page
                console.log("💪 Workout plan received (ignoring)");
              } else if (data.event === "error") {
                console.error("❌ Error:", data.message);
                setStatus(`Error: ${data.message}`);
                setIsGenerating(false);
              }
            } catch (e) {
              console.error("⚠️ Error parsing SSE data:", e);
            }
          }
        }
      }
    } catch (error) {
      console.error("❌ Error generating meal plan:", error);
      setStatus("Failed to generate meal plan");
      setIsGenerating(false);
    }
  };

  return (
    <>
      <GoalsInputModal
        isOpen={showGoalsModal}
        onClose={() => {
          setShowGoalsModal(false);
          router.push("/dashboard");
        }}
        onSubmit={handleGoalsSubmit}
        bodyType={bodyType}
      />
      <div className="min-h-screen bg-gradient-to-br from-purple-900 via-gray-900 to-pink-900 text-white">
        <div className="container mx-auto px-4 py-8 max-w-5xl">
          {/* Header */}
          <div className="flex items-center justify-between mb-8">
            <button
              onClick={() => {
                // Allow user to update goals
                setShowGoalsModal(true);
              }}
              className="px-4 py-2 bg-white/10 hover:bg-white/20 backdrop-blur-lg rounded-full font-semibold transition-all duration-300 text-sm"
              title="Update your fitness goals"
            >
              ✏️ Update Goals
            </button>
            <button
              onClick={() => router.push("/dashboard")}
              className="px-6 py-3 bg-white/10 hover:bg-white/20 backdrop-blur-lg rounded-full font-semibold transition-all duration-300 hover:scale-105"
            >
              ← Back to Dashboard
            </button>
          </div>

        {/* Title */}
        <div className="text-center mb-8">
          <h1 className="text-5xl font-bold mb-4 bg-gradient-to-r from-purple-400 to-pink-400 bg-clip-text text-transparent">
            Your Meal Plan
          </h1>
          <p className="text-xl text-gray-300">{status}</p>
        </div>

        {/* Loading State */}
        {isGenerating && (
          <div className="flex flex-col items-center justify-center py-20 gap-4">
            <div className="relative">
              <div className="w-20 h-20 border-4 border-purple-500 border-t-transparent rounded-full animate-spin"></div>
              <div className="absolute inset-0 w-20 h-20 border-4 border-pink-500 border-t-transparent rounded-full animate-spin opacity-50" style={{ animationDirection: "reverse" }}></div>
            </div>
            <p className="text-gray-400">This may take 1-2 minutes...</p>
          </div>
        )}

        {/* Plan Content */}
        {plan && (
          <div className="bg-white/10 backdrop-blur-lg rounded-3xl p-8 border border-white/20 shadow-2xl">
            <div className="prose prose-invert prose-lg max-w-none
              prose-headings:text-purple-300 
              prose-h1:text-4xl prose-h1:font-bold prose-h1:mb-6
              prose-h2:text-3xl prose-h2:font-bold prose-h2:text-pink-300 prose-h2:mt-8 prose-h2:mb-4
              prose-h3:text-2xl prose-h3:font-semibold prose-h3:text-purple-200 prose-h3:mt-6 prose-h3:mb-3
              prose-p:text-gray-200 prose-p:leading-relaxed prose-p:mb-4
              prose-strong:text-white prose-strong:font-bold
              prose-ul:text-gray-200 prose-ul:my-4
              prose-li:text-gray-300 prose-li:my-2
              prose-ol:text-gray-200 prose-ol:my-4
              prose-code:text-pink-300 prose-code:bg-white/10 prose-code:px-2 prose-code:py-1 prose-code:rounded prose-code:text-sm
              prose-blockquote:text-gray-300 prose-blockquote:border-purple-500 prose-blockquote:pl-4 prose-blockquote:italic
              prose-a:text-purple-400 prose-a:hover:text-pink-400
              prose-hr:border-gray-600 prose-hr:my-8
              prose-table:text-gray-200 prose-th:bg-white/10 prose-th:p-3 prose-td:p-3 prose-td:border-gray-700
            ">
              <ReactMarkdown remarkPlugins={[remarkGfm]}>
                {plan}
              </ReactMarkdown>
            </div>
          </div>
        )}

        {/* Empty State */}
        {!plan && !isGenerating && (
          <div className="text-center py-20">
            <p className="text-xl text-gray-400">No meal plan available</p>
            <button
              onClick={() => {
                const storedGoals = localStorage.getItem("userGoals");
                if (!storedGoals) {
                  setShowGoalsModal(true);
                } else {
                  generateMealPlan();
                }
              }}
              className="mt-6 px-8 py-3 bg-gradient-to-r from-purple-500 to-pink-500 hover:from-purple-600 hover:to-pink-600 rounded-full font-semibold transition-all duration-300 hover:scale-105"
            >
              Generate Meal Plan
            </button>
          </div>
        )}
      </div>
    </div>
    </>
  );
}

