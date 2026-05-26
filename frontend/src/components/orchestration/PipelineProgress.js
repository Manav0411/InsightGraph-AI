import React from 'react';

export default function PipelineProgress({ active, progressData }) {
  if (!active) return null;

  const isComplete = progressData?.stage === 'Complete';

  return (
    <div className="fixed inset-0 bg-black/60 backdrop-blur-sm z-[100] flex items-center justify-center p-4 sm:p-8">
      <style dangerouslySetInnerHTML={{__html: `
        .dark-modal {
            background-color: #2e3230;
            color: #faf6f0;
            box-shadow: 0 10px 40px rgba(0, 0, 0, 0.4);
        }
        .pulse-ring {
            animation: pulse-ring 2s cubic-bezier(0.215, 0.61, 0.355, 1) infinite;
        }
        @keyframes pulse-ring {
            0% { transform: scale(0.95); opacity: 0.5; box-shadow: 0 0 0 0 rgba(74, 124, 89, 0.4); }
            70% { transform: scale(1); opacity: 1; box-shadow: 0 0 0 10px rgba(74, 124, 89, 0); }
            100% { transform: scale(0.95); opacity: 0.5; box-shadow: 0 0 0 0 rgba(74, 124, 89, 0); }
        }
        .shimmer {
            background: linear-gradient(90deg, rgba(255,255,255,0) 0%, rgba(255,255,255,0.05) 50%, rgba(255,255,255,0) 100%);
            background-size: 200% 100%;
            animation: shimmer 2s infinite linear;
        }
        @keyframes shimmer {
            0% { background-position: -200% 0; }
            100% { background-position: 200% 0; }
        }
        .glow-active {
            box-shadow: 0 0 15px rgba(142, 207, 158, 0.6), inset 0 0 10px rgba(142, 207, 158, 0.4);
        }
      `}} />

      {/* Modal Container */}
      <div className="dark-modal w-full max-w-[500px] rounded-2xl overflow-hidden flex flex-col relative border border-outline-variant/20 transition-all duration-500">
        
        {/* Shimmer Effect across top */}
        <div className="absolute top-0 left-0 right-0 h-1 bg-gradient-to-r from-transparent via-primary/50 to-transparent opacity-50 shimmer"></div>
        
        {/* Header */}
        <div className="p-6 pb-4 flex justify-between items-start border-b border-white/10">
          <div>
            <h2 className="font-headline text-xl font-bold tracking-wide text-white mb-1">
              {isComplete ? 'Intelligence Briefing Synthesized' : 'Pipeline Execution'}
            </h2>
            <p className="font-label text-sm text-white/60">
              {isComplete ? 'Execution successful. Redirecting...' : 'Orchestrating AI agents...'}
            </p>
          </div>
        </div>
        
        {/* Content Area */}
        <div className="p-6 flex flex-col gap-8 relative min-h-[350px] justify-center">
          
          {isComplete ? (
            <div className="flex flex-col items-center justify-center text-center animate-in fade-in zoom-in duration-500">
              <div className="w-24 h-24 bg-primary/20 rounded-full flex items-center justify-center mb-6 relative">
                <div className="absolute inset-0 bg-primary/20 rounded-full animate-ping"></div>
                <span className="material-symbols-outlined text-5xl text-primary relative z-10">task_alt</span>
              </div>
              <h3 className="font-headline text-2xl font-bold text-white mb-2">Signal Processing Complete</h3>
              <p className="text-white/80 text-sm max-w-[80%] mx-auto mb-6">
                Intelligence signals retrieved, grounded, and synthesized successfully.
              </p>
              <div className="flex gap-4 w-full">
                <div className="bg-[#1e2220] flex-1 rounded-xl p-4 border border-white/10 text-center">
                  <div className="text-xs text-white/50 uppercase tracking-wider mb-1">Time</div>
                  <div className="text-lg font-bold text-[#8ecf9e]">{progressData?.elapsed || '0.0s'}</div>
                </div>
                <div className="bg-[#1e2220] flex-1 rounded-xl p-4 border border-white/10 text-center">
                  <div className="text-xs text-white/50 uppercase tracking-wider mb-1">Status</div>
                  <div className="text-lg font-bold text-primary">Grounded</div>
                </div>
              </div>
            </div>
          ) : (
            <>
              {/* Central Progress Ring */}
              <div className="flex justify-center relative py-4">
                <div className="relative w-32 h-32 flex items-center justify-center">
                  <svg className="absolute inset-0 w-full h-full transform -rotate-90" viewBox="0 0 100 100">
                    <circle cx="50" cy="50" fill="none" r="45" stroke="rgba(228, 224, 216, 0.1)" strokeLinecap="round" strokeWidth="8"></circle>
                    <circle className="transition-all duration-1000 ease-out drop-shadow-[0_0_8px_rgba(142,207,158,0.4)]" cx="50" cy="50" fill="none" r="45" stroke="#8ecf9e" strokeDasharray="282.74" strokeDashoffset={282.74 - (282.74 * (progressData?.progress || 0)) / 100} strokeLinecap="round" strokeWidth="8"></circle>
                  </svg>
                  <div className="absolute inset-2 rounded-full pulse-ring pointer-events-none"></div>
                  <div className="text-center z-10 flex flex-col items-center justify-center w-full h-full bg-[#1e2220] rounded-full border border-white/5 shadow-inner">
                    <span className="font-headline text-3xl font-bold text-[#8ecf9e] leading-none">{Math.round(progressData?.progress || 0)}<span className="text-lg text-[#8ecf9e]/80">%</span></span>
                    <span className="font-label text-xs text-white/50 mt-1 uppercase tracking-wider">{progressData?.stage || 'Active'}</span>
                  </div>
                </div>
              </div>
              
              {/* Vertical Stepper */}
              <div className="flex flex-col gap-4 relative">
                <div className="absolute left-3.5 top-4 bottom-4 w-px bg-white/10 z-0"></div>
                
                <div className={`flex items-start gap-4 relative z-10 transition-opacity duration-300 ${progressData?.progress >= 16 ? 'opacity-100' : 'opacity-40'}`}>
                  <div className={`mt-0.5 w-7 h-7 rounded-full flex items-center justify-center shrink-0 transition-all duration-300 ${progressData?.progress >= 33 ? 'bg-[#8ecf9e]/20 border border-[#8ecf9e]' : 'bg-[#1e2220] border-2 border-[#8ecf9e] glow-active'}`}>
                    {progressData?.progress >= 33 ? <span className="material-symbols-outlined text-[16px] text-[#8ecf9e]">check</span> : <div className="w-2.5 h-2.5 rounded-full bg-[#8ecf9e] animate-pulse"></div>}
                  </div>
                  <div className="flex-1">
                    <h4 className={`font-body font-bold text-base transition-colors duration-300 ${progressData?.progress >= 33 ? 'text-white/80 text-sm' : 'text-[#8ecf9e]'}`}>Data Ingestion</h4>
                    <p className="font-label text-xs text-white/60 mt-0.5">Retrieving intelligence sources.</p>
                  </div>
                </div>
                
                <div className={`flex items-start gap-4 relative z-10 transition-opacity duration-300 ${progressData?.progress >= 33 ? 'opacity-100' : 'opacity-40'}`}>
                  <div className={`mt-0.5 w-7 h-7 rounded-full flex items-center justify-center shrink-0 transition-all duration-300 ${progressData?.progress >= 66 ? 'bg-[#8ecf9e]/20 border border-[#8ecf9e]' : progressData?.progress >= 33 ? 'bg-[#1e2220] border-2 border-[#8ecf9e] glow-active' : 'bg-[#1e2220] border-2 border-white/20'}`}>
                    {progressData?.progress >= 66 ? <span className="material-symbols-outlined text-[16px] text-[#8ecf9e]">check</span> : progressData?.progress >= 33 ? <div className="w-2.5 h-2.5 rounded-full bg-[#8ecf9e] animate-pulse"></div> : <span className="material-symbols-outlined text-[16px] text-white/30">hourglass_empty</span>}
                  </div>
                  <div className="flex-1">
                    <h4 className={`font-body font-bold text-base transition-colors duration-300 ${progressData?.progress >= 66 ? 'text-white/80 text-sm' : progressData?.progress >= 33 ? 'text-[#8ecf9e]' : 'text-white/80 text-sm'}`}>Grounding & Validation</h4>
                    <p className="font-label text-sm text-white/60 mt-0.5">Checking facts against trusted sources.</p>
                  </div>
                </div>
                
                <div className={`flex items-start gap-4 relative z-10 transition-opacity duration-300 ${progressData?.progress >= 66 ? 'opacity-100' : 'opacity-40'}`}>
                  <div className={`mt-0.5 w-7 h-7 rounded-full flex items-center justify-center shrink-0 transition-all duration-300 ${progressData?.progress >= 100 ? 'bg-[#8ecf9e]/20 border border-[#8ecf9e]' : progressData?.progress >= 66 ? 'bg-[#1e2220] border-2 border-[#8ecf9e] glow-active' : 'bg-[#1e2220] border-2 border-white/20'}`}>
                    {progressData?.progress >= 100 ? <span className="material-symbols-outlined text-[16px] text-[#8ecf9e]">check</span> : progressData?.progress >= 66 ? <div className="w-2.5 h-2.5 rounded-full bg-[#8ecf9e] animate-pulse"></div> : <span className="material-symbols-outlined text-[16px] text-white/30">hourglass_empty</span>}
                  </div>
                  <div className="flex-1">
                    <h4 className={`font-body font-bold text-base transition-colors duration-300 ${progressData?.progress >= 100 ? 'text-white/80 text-sm' : progressData?.progress >= 66 ? 'text-[#8ecf9e]' : 'text-white/80 text-sm'}`}>Synthesis & Delivery</h4>
                    <p className="font-label text-xs text-white/60 mt-0.5">Drafting final briefing.</p>
                  </div>
                </div>
              </div>
              
              {/* Terminal / Log Output */}
              <div className="bg-black/40 rounded-xl p-4 border border-white/5 shadow-inner overflow-hidden relative group mt-4">
                <div className="absolute top-0 right-4 px-2 py-1 bg-[#1e2220] rounded-b-md border-x border-b border-white/5 font-mono text-[10px] text-white/30 tracking-widest uppercase">System Log</div>
                <div className="font-mono text-xs leading-relaxed text-white/70 flex flex-col gap-1 mt-2">
                  <div className="flex gap-2"><span className="text-white/40">[SYS]</span><span className="text-white/50">INIT</span><span>Starting graph traversal...</span></div>
                  {progressData?.log?.map((logItem, i) => (
                    <div key={i} className="flex gap-2"><span className="text-white/40">[AGENT]</span><span className="text-[#8ecf9e]">INFO</span><span>{logItem.replace('[AGENT] INFO: ', '')}</span></div>
                  ))}
                  <div className="flex gap-2 items-center"><span className="text-white/40">[AGENT]</span><span className="text-[#8ecf9e]">INFO</span><span>Processing...</span><span className="w-1.5 h-3 bg-[#8ecf9e]/70 animate-pulse ml-1"></span></div>
                </div>
              </div>
            </>
          )}
          
        </div>
        
        {/* Footer */}
        {!isComplete && (
          <div className="bg-black/20 p-4 border-t border-white/5 flex justify-between items-center rounded-b-2xl">
            <div className="flex items-center gap-2 text-white/50 font-mono text-xs">
              <span className="material-symbols-outlined text-[14px]">timer</span>
              <span>Elapsed: {progressData?.elapsed || '0.0s'}</span>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
