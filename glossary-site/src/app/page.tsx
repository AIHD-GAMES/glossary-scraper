import GlossaryUI from '@/components/GlossaryUI';
import { Sparkles } from 'lucide-react';

export default function Home() {
  return (
    <main className="min-h-screen bg-white">
      {/* Hero Section */}
      <div className="relative overflow-hidden pt-16 pb-24 sm:pt-24 sm:pb-32">
        <div className="absolute top-0 left-1/2 -translate-x-1/2 w-[1000px] h-[600px] bg-indigo-500/10 blur-[120px] rounded-full pointer-events-none"></div>

        <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <h1 className="text-5xl sm:text-6xl font-black text-[#1a4696] mb-6 tracking-tight">
            投資部 用語集
          </h1>
          <p className="text-xl text-slate-600 max-w-2xl mx-auto leading-relaxed font-bold">
            講義でわからない投資用語をすぐに調べられます。
          </p>
        </div>
      </div>

      {/* Main UI */}
      <GlossaryUI />

      {/* Footer */}
      <footer className="mt-32 border-t border-slate-100 dark:border-slate-800 py-12 bg-slate-50 dark:bg-slate-900/50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <p className="text-slate-500 text-sm italic mb-4">
            ※本用語集は一般的な解説を目的としており、特定の投資を勧誘するものではありません。
          </p>
          <p className="text-slate-400 text-sm">
            &copy; {new Date().getFullYear()} 投資部. All rights reserved.
          </p>
        </div>
      </footer>
    </main>
  );
}
