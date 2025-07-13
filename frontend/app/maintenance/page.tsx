import { Metadata } from "next";
import { Public_Sans } from "next/font/google";

const publicSans = Public_Sans({
  weight: ["300", "400", "500", "600", "700"],
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "Under Maintenance - AI IELTS Examiner",
  description: "We're making improvements to serve you better. Please check back soon.",
};

export default function MaintenancePage() {
  return (
    <div className={`fixed inset-0 z-50 flex items-center justify-center bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 ${publicSans.className}`}>
      {/* Animated background elements */}
      <div className="absolute inset-0 overflow-hidden">
        <div className="absolute -top-1/2 -left-1/2 w-96 h-96 bg-gradient-to-br from-purple-500/30 to-pink-500/30 rounded-full blur-3xl animate-pulse"></div>
        <div className="absolute -bottom-1/2 -right-1/2 w-96 h-96 bg-gradient-to-br from-blue-500/30 to-cyan-500/30 rounded-full blur-3xl animate-pulse delay-1000"></div>
        <div className="absolute top-1/4 right-1/4 w-64 h-64 bg-gradient-to-br from-indigo-500/20 to-purple-500/20 rounded-full blur-2xl animate-pulse delay-500"></div>
      </div>

      {/* Main content */}
      <div className="relative z-10 text-center px-8 max-w-4xl mx-auto">
        {/* Logo/Brand area */}
        <div className="mb-12">
          <div className="inline-flex items-center justify-center w-24 h-24 bg-gradient-to-br from-purple-500 to-pink-500 rounded-2xl shadow-2xl mb-8 animate-bounce">
            <svg className="w-12 h-12 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
            </svg>
          </div>
          <h1 className="text-4xl md:text-6xl font-light text-white mb-4 tracking-tight">
            AI IELTS Examiner
          </h1>
          <div className="w-24 h-1 bg-gradient-to-r from-purple-500 to-pink-500 mx-auto rounded-full"></div>
        </div>

        {/* Maintenance message */}
        <div className="mb-12 space-y-6">
          <h2 className="text-3xl md:text-4xl font-light text-white mb-6 tracking-tight">
            Elevating Your Experience
          </h2>
          <p className="text-xl md:text-2xl text-gray-300 font-light leading-relaxed max-w-2xl mx-auto">
            We&apos;re crafting something extraordinary. Our platform is undergoing premium enhancements to deliver an even more exceptional learning experience.
          </p>
        </div>

        {/* Countdown/Timeline */}
        <div className="mb-12">
          <div className="bg-white/5 backdrop-blur-lg rounded-3xl p-8 shadow-2xl border border-white/10">
            <div className="flex items-center justify-center space-x-4 mb-6">
              <div className="w-3 h-3 bg-yellow-400 rounded-full animate-pulse"></div>
              <span className="text-lg font-medium text-gray-300">Maintenance in Progress</span>
            </div>
            
            <div className="space-y-4">
              <p className="text-2xl font-light text-white">
                We&apos;ll be back online at
              </p>
              <div className="text-4xl md:text-5xl font-medium text-transparent bg-clip-text bg-gradient-to-r from-purple-400 to-pink-400">
                6:00 PM
              </div>
              <div className="text-xl text-gray-300">
                July 13th, 2025
              </div>
            </div>
          </div>
        </div>

      </div>

      {/* Subtle animation overlay */}
      <div className="absolute inset-0 bg-gradient-to-t from-black/20 via-transparent to-black/20 pointer-events-none"></div>
    </div>
  );
} 