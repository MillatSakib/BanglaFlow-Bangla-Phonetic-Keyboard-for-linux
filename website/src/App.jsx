import React, { useState, useEffect } from 'react';
import { 
  Download, Terminal, Check, Copy, ExternalLink, ShieldCheck, Zap, 
  Keyboard, Sparkles, Cpu, BookOpen, Layers, ArrowRight, Star, 
  Monitor, CheckCircle2, AlertCircle, RefreshCw, ChevronRight, Hash
} from 'lucide-react';
import { transliterate } from './phonetic.js';

const GITHUB_REPO = "MillatSakib/BanglaFlow-Bangla-Phonetic-Keyboard-for-linux";

const PRESET_PHRASES = [
  "amar sonar bangla ami",
  "ami bangla valobashi",
  "tumi kemon acho?",
  "banglaflow",
  "dhonnobad",
  "du:kho"
];

export default function App() {
  const [copiedCmd, setCopiedCmd] = useState(null);
  const [demoInput, setDemoInput] = useState("amar sonar bangla ami");
  const [demoOutput, setDemoOutput] = useState("");
  const [installTab, setInstallTab] = useState("deb");
  const [cheatTab, setCheatTab] = useState("vowels");

  // Dynamic GitHub Release State
  const [releaseInfo, setReleaseInfo] = useState({
    version: "v1.0.1",
    debFileName: "banglaflow_1.0.1.deb",
    debUrl: `https://github.com/${GITHUB_REPO}/releases/download/v1.0.1/banglaflow_1.0.1.deb`,
    releasePageUrl: `https://github.com/${GITHUB_REPO}/releases/latest`
  });

  // Fetch latest release dynamically from GitHub API
  useEffect(() => {
    async function fetchLatestRelease() {
      try {
        const res = await fetch(`https://api.github.com/repos/${GITHUB_REPO}/releases/latest`);
        if (!res.ok) return;
        const data = await res.json();
        if (data && data.tag_name) {
          const debAsset = data.assets && data.assets.find(a => a.name.endsWith('.deb'));
          const cleanVer = data.tag_name.replace(/^v/, '');
          setReleaseInfo({
            version: data.tag_name,
            debFileName: debAsset ? debAsset.name : `banglaflow_${cleanVer}.deb`,
            debUrl: debAsset ? debAsset.browser_download_url : `https://github.com/${GITHUB_REPO}/releases/download/${data.tag_name}/banglaflow_${cleanVer}.deb`,
            releasePageUrl: data.html_url || `https://github.com/${GITHUB_REPO}/releases/latest`
          });
        }
      } catch (e) {
        console.warn("Could not fetch latest release from GitHub API, using fallback:", e);
      }
    }
    fetchLatestRelease();
  }, []);

  // Live transliteration update
  useEffect(() => {
    setDemoOutput(transliterate(demoInput));
  }, [demoInput]);

  const copyToClipboard = (text, id) => {
    navigator.clipboard.writeText(text);
    setCopiedCmd(id);
    setTimeout(() => setCopiedCmd(null), 2000);
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 selection:bg-emerald-500 selection:text-white relative">
      {/* Background glowing ambient orbs */}
      <div className="fixed top-0 left-1/4 w-96 h-96 bg-emerald-500/10 rounded-full blur-3xl pointer-events-none -z-10 animate-pulse"></div>
      <div className="fixed bottom-1/4 right-1/4 w-[32rem] h-[32rem] bg-cyan-500/10 rounded-full blur-3xl pointer-events-none -z-10"></div>
      <div className="fixed top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[40rem] h-[40rem] bg-teal-500/5 rounded-full blur-[140px] pointer-events-none -z-10"></div>

      {/* Navigation */}
      <header className="sticky top-0 z-50 glass-panel border-b border-white/5">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-20 flex items-center justify-between">
          <a href="#" className="flex items-center gap-3 group">
            <div className="w-11 h-11 rounded-xl bg-gradient-to-tr from-emerald-500 to-cyan-500 p-0.5 shadow-lg shadow-emerald-500/20 group-hover:scale-105 transition-transform duration-300">
              <img src="./logo.png" alt="BanglaFlow Logo" className="w-full h-full object-cover rounded-[10px]" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <span className="font-extrabold text-xl tracking-tight bg-gradient-to-r from-white via-slate-100 to-slate-300 bg-clip-text text-transparent">BanglaFlow</span>
                <span className="px-2 py-0.5 text-xs font-semibold bg-emerald-500/20 text-emerald-400 border border-emerald-500/30 rounded-full">
                  {releaseInfo.version}
                </span>
              </div>
              <p className="text-[11px] text-slate-400">Native Bengali Keyboard for Linux</p>
            </div>
          </a>

          <nav className="hidden md:flex items-center gap-8 text-sm font-medium text-slate-300">
            <a href="#features" className="hover:text-emerald-400 transition-colors">Features</a>
            <a href="#sandbox" className="hover:text-emerald-400 transition-colors">Live Sandbox</a>
            <a href="#cheatsheet" className="hover:text-emerald-400 transition-colors">Cheat Sheet</a>
            <a href="#comparison" className="hover:text-emerald-400 transition-colors">Comparison</a>
            <a href="#install" className="hover:text-emerald-400 transition-colors">Install</a>
          </nav>

          <div className="flex items-center gap-3">
            <a 
              href={`https://github.com/${GITHUB_REPO}`} 
              target="_blank" 
              rel="noreferrer"
              className="p-2.5 rounded-xl glass-card text-slate-300 hover:text-white hover:border-emerald-500/40 transition-all flex items-center gap-2 text-sm"
              title="GitHub Repository"
            >
              <Star className="w-4 h-4 text-amber-400 fill-amber-400/30" />
              <span className="hidden sm:inline font-mono">GitHub</span>
            </a>
            <a 
              href={releaseInfo.debUrl}
              download
              className="px-4 py-2.5 rounded-xl bg-gradient-to-r from-emerald-500 to-teal-500 hover:from-emerald-400 hover:to-teal-400 text-slate-950 font-bold text-sm shadow-lg shadow-emerald-500/20 hover:shadow-emerald-500/30 hover:scale-[1.02] active:scale-[0.98] transition-all flex items-center gap-2"
              title={`Download latest Debian package (${releaseInfo.version})`}
            >
              <Download className="w-4 h-4" />
              <span>Get {releaseInfo.version}</span>
            </a>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <section className="relative pt-16 pb-20 md:pt-24 md:pb-28 overflow-hidden">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center max-w-3xl mx-auto">
            <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full glass-card border border-emerald-500/30 text-emerald-300 text-xs sm:text-sm font-medium mb-8 glow-emerald">
              <span className="w-2 h-2 rounded-full bg-emerald-400 animate-ping"></span>
              Built Natively for Ubuntu GNOME (Wayland & X11)
            </div>

            <h1 className="text-4xl sm:text-5xl md:text-6xl lg:text-7xl font-extrabold tracking-tight text-white leading-[1.12]">
              Bengali Phonetic Typing on Linux,{' '}
              <span className="bg-gradient-to-r from-emerald-400 via-teal-300 to-cyan-400 bg-clip-text text-transparent">
                Reimagined.
              </span>
            </h1>

            <p className="mt-6 text-base sm:text-lg md:text-xl text-slate-300 leading-relaxed max-w-2xl mx-auto">
              Blazing fast, 100% offline, zero switch delay, and full Avro phonetic layout compatibility. Experience effortless Bengali typing natively on modern Linux.
            </p>

            {/* CTAs */}
            <div className="mt-10 flex flex-col sm:flex-row items-center justify-center gap-4">
              <a 
                href={releaseInfo.debUrl}
                download
                className="w-full sm:w-auto px-8 py-4 rounded-xl bg-gradient-to-r from-emerald-500 to-teal-500 hover:from-emerald-400 hover:to-teal-400 text-slate-950 font-extrabold text-base shadow-xl shadow-emerald-500/25 hover:shadow-emerald-500/40 hover:-translate-y-0.5 transition-all flex items-center justify-center gap-3"
              >
                <Download className="w-5 h-5" />
                <span>Download .deb ({releaseInfo.version})</span>
              </a>

              <a 
                href="#snap-install"
                className="w-full sm:w-auto px-7 py-4 rounded-xl glass-panel hover:bg-slate-800/80 text-white font-semibold text-base border border-white/10 hover:border-emerald-500/40 transition-all flex items-center justify-center gap-2.5"
              >
                <Terminal className="w-5 h-5 text-cyan-400" />
                <span>Install via Snap</span>
              </a>
            </div>

            {/* Key Specs Pills */}
            <div className="mt-12 flex flex-wrap items-center justify-center gap-3 text-xs sm:text-sm text-slate-400">
              <span className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-slate-900/60 border border-slate-800">
                <Check className="w-4 h-4 text-emerald-400" /> 177,000+ Dictionary Cache
              </span>
              <span className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-slate-900/60 border border-slate-800">
                <Check className="w-4 h-4 text-emerald-400" /> 0.001s Zero Delay Switch
              </span>
              <span className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-slate-900/60 border border-slate-800">
                <Check className="w-4 h-4 text-emerald-400" /> 100% Offline & Private
              </span>
              <span className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-slate-900/60 border border-slate-800">
                <Check className="w-4 h-4 text-emerald-400" /> GPL-3.0 Open Source
              </span>
            </div>
          </div>

          {/* Interactive Live Sandbox */}
          <div id="sandbox" className="mt-16 sm:mt-20 max-w-4xl mx-auto">
            <div className="glass-panel rounded-2xl p-6 sm:p-8 shadow-2xl border border-white/10 relative glow-cyan">
              <div className="flex items-center justify-between pb-6 border-b border-white/5">
                <div className="flex items-center gap-3">
                  <div className="flex gap-1.5">
                    <span className="w-3 h-3 rounded-full bg-rose-500/80"></span>
                    <span className="w-3 h-3 rounded-full bg-amber-500/80"></span>
                    <span className="w-3 h-3 rounded-full bg-emerald-500/80"></span>
                  </div>
                  <span className="text-xs font-mono text-slate-400 ml-2">BanglaFlow Live Typing Sandbox</span>
                </div>
                <div className="flex items-center gap-2">
                  <span className="px-2.5 py-1 rounded-md text-xs font-mono bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                    Engine: Active [bn]
                  </span>
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mt-6">
                <div>
                  <label className="block text-xs font-semibold uppercase tracking-wider text-slate-400 mb-2">
                    Type Banglish / English Phonetic:
                  </label>
                  <div className="relative">
                    <input 
                      type="text" 
                      value={demoInput}
                      onChange={(e) => setDemoInput(e.target.value)}
                      placeholder="Type e.g. amar sonar bangla ami..."
                      className="w-full px-4 py-3.5 rounded-xl bg-slate-900/90 border border-slate-700/80 text-white font-mono text-base focus:outline-none focus:border-emerald-500 focus:ring-2 focus:ring-emerald-500/20 transition-all placeholder:text-slate-600"
                    />
                    {demoInput && (
                      <button 
                        onClick={() => setDemoInput("")} 
                        className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-500 hover:text-slate-300 text-xs px-2 py-1 rounded bg-slate-800"
                      >
                        Clear
                      </button>
                    )}
                  </div>

                  {/* Preset quick test tags */}
                  <div className="mt-3 flex flex-wrap gap-1.5 items-center">
                    <span className="text-[11px] text-slate-500">Try quick phrases:</span>
                    {PRESET_PHRASES.map((phrase) => (
                      <button
                        key={phrase}
                        onClick={() => setDemoInput(phrase)}
                        className="text-xs px-2 py-0.5 rounded bg-slate-800/80 hover:bg-emerald-500/20 hover:text-emerald-300 text-slate-400 border border-slate-700/50 transition-colors font-mono"
                      >
                        {phrase}
                      </button>
                    ))}
                  </div>
                </div>

                <div>
                  <label className="block text-xs font-semibold uppercase tracking-wider text-emerald-400 mb-2">
                    Instant Bengali Output:
                  </label>
                  <div className="w-full px-4 py-3.5 rounded-xl bg-slate-900/50 border border-emerald-500/30 text-emerald-300 font-bengali text-2xl font-semibold min-h-[54px] flex items-center justify-between shadow-inner">
                    <span>{demoOutput || <span className="text-slate-600 font-sans text-sm font-normal">Transliterated text will appear here...</span>}</span>
                    {demoOutput && (
                      <button 
                        onClick={() => copyToClipboard(demoOutput, 'demo')}
                        className="p-1.5 rounded-lg bg-emerald-500/10 hover:bg-emerald-500/20 text-emerald-400 transition-colors ml-2 flex-shrink-0"
                        title="Copy text"
                      >
                        {copiedCmd === 'demo' ? <Check className="w-4 h-4 text-emerald-400" /> : <Copy className="w-4 h-4" />}
                      </button>
                    )}
                  </div>
                  <p className="mt-2 text-xs text-slate-400 flex items-center gap-1.5">
                    <Sparkles className="w-3.5 h-3.5 text-cyan-400" />
                    Matches longest-match phonetic rule tables + 177k dictionary ranking.
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Features Grid */}
      <section id="features" className="py-20 sm:py-24 border-t border-white/5 relative">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center max-w-2xl mx-auto mb-16">
            <h2 className="text-xs sm:text-sm font-bold uppercase tracking-widest text-emerald-400 mb-3">Engine Highlights</h2>
            <p className="text-3xl sm:text-4xl font-extrabold text-white tracking-tight">
              Engineered with Precision for Linux Power Users
            </p>
            <p className="mt-4 text-slate-400 text-base">
              Say goodbye to cursor jumping, switch lag, and erased words. BanglaFlow is built from the ground up to respect your workflow.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 sm:gap-8">
            {/* Feature 1 */}
            <div className="glass-card p-6 sm:p-8 rounded-2xl hover:border-emerald-500/40 transition-all duration-300 group hover:-translate-y-1">
              <div className="w-12 h-12 rounded-xl bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 flex items-center justify-center mb-6 group-hover:scale-110 transition-transform">
                <Zap className="w-6 h-6" />
              </div>
              <h3 className="text-xl font-bold text-white mb-2">Zero-Delay Keyboard Switch</h3>
              <p className="text-sm text-slate-400 leading-relaxed">
                Switches in 0.001 seconds without typing delay or English letter leakage, using a pre-warmed binary dictionary cache.
              </p>
            </div>

            {/* Feature 2 */}
            <div className="glass-card p-6 sm:p-8 rounded-2xl hover:border-cyan-500/40 transition-all duration-300 group hover:-translate-y-1">
              <div className="w-12 h-12 rounded-xl bg-cyan-500/10 text-cyan-400 border border-cyan-500/20 flex items-center justify-center mb-6 group-hover:scale-110 transition-transform">
                <BookOpen className="w-6 h-6" />
              </div>
              <h3 className="text-xl font-bold text-white mb-2">177,000+ Word Dictionary</h3>
              <p className="text-sm text-slate-400 leading-relaxed">
                Pre-compiled offline Bengali dictionary ranking exact matches, phonetic candidates, and intelligent prefix auto-completion.
              </p>
            </div>

            {/* Feature 3 */}
            <div className="glass-card p-6 sm:p-8 rounded-2xl hover:border-teal-500/40 transition-all duration-300 group hover:-translate-y-1">
              <div className="w-12 h-12 rounded-xl bg-teal-500/10 text-teal-400 border border-teal-500/20 flex items-center justify-center mb-6 group-hover:scale-110 transition-transform">
                <ShieldCheck className="w-6 h-6" />
              </div>
              <h3 className="text-xl font-bold text-white mb-2">100% Offline & Zero Telemetry</h3>
              <p className="text-sm text-slate-400 leading-relaxed">
                Completely self-contained. No background analytics, no cloud calls, and zero external network traffic. Your keystrokes stay strictly private.
              </p>
            </div>

            {/* Feature 4 */}
            <div className="glass-card p-6 sm:p-8 rounded-2xl hover:border-emerald-500/40 transition-all duration-300 group hover:-translate-y-1">
              <div className="w-12 h-12 rounded-xl bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 flex items-center justify-center mb-6 group-hover:scale-110 transition-transform">
                <Keyboard className="w-6 h-6" />
              </div>
              <h3 className="text-xl font-bold text-white mb-2">Native System Keys Intact</h3>
              <p className="text-sm text-slate-400 leading-relaxed">
                F1 through F12, Escape, Delete, PrintScreen, ScrollLock, and window manager shortcuts pass directly to Linux without interception.
              </p>
            </div>

            {/* Feature 5 */}
            <div className="glass-card p-6 sm:p-8 rounded-2xl hover:border-cyan-500/40 transition-all duration-300 group hover:-translate-y-1">
              <div className="w-12 h-12 rounded-xl bg-cyan-500/10 text-cyan-400 border border-cyan-500/20 flex items-center justify-center mb-6 group-hover:scale-110 transition-transform">
                <Hash className="w-6 h-6" />
              </div>
              <h3 className="text-xl font-bold text-white mb-2">Direct Digit Output</h3>
              <p className="text-sm text-slate-400 leading-relaxed">
                Top-row and NumPad numbers 0-9 unconditionally type numerals without candidate list hijacking. Toggle Bengali or English digits on demand.
              </p>
            </div>

            {/* Feature 6 */}
            <div className="glass-card p-6 sm:p-8 rounded-2xl hover:border-teal-500/40 transition-all duration-300 group hover:-translate-y-1">
              <div className="w-12 h-12 rounded-xl bg-teal-500/10 text-teal-400 border border-teal-500/20 flex items-center justify-center mb-6 group-hover:scale-110 transition-transform">
                <Monitor className="w-6 h-6" />
              </div>
              <h3 className="text-xl font-bold text-white mb-2">Wayland & X11 Native</h3>
              <p className="text-sm text-slate-400 leading-relaxed">
                Designed natively for the modern IBus input framework with clean top-panel indicator symbol (`bn`) on Ubuntu 24.04 and 26.04 LTS.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Comparison Table Section */}
      <section id="comparison" className="py-20 sm:py-24 bg-slate-900/30 border-t border-white/5">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center max-w-2xl mx-auto mb-16">
            <h2 className="text-xs sm:text-sm font-bold uppercase tracking-widest text-emerald-400 mb-3">Direct Comparison</h2>
            <p className="text-3xl sm:text-4xl font-extrabold text-white tracking-tight">
              Why BanglaFlow Outperforms Existing Linux Input Methods
            </p>
          </div>

          <div className="glass-panel rounded-2xl overflow-x-auto border border-white/10 shadow-xl">
            <table className="w-full text-left text-sm">
              <thead className="bg-slate-900/90 text-slate-300 font-semibold border-b border-white/10">
                <tr>
                  <th className="py-4 px-6">Feature</th>
                  <th className="py-4 px-6 text-emerald-400 font-bold text-base">BanglaFlow ({releaseInfo.version})</th>
                  <th className="py-4 px-6 text-slate-400">Legacy IBus-Avro</th>
                  <th className="py-4 px-6 text-slate-400">Generic OpenBhasha</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-white/5 text-slate-300">
                <tr className="hover:bg-slate-800/30 transition-colors">
                  <td className="py-4 px-6 font-medium">Switch Delay (Lag)</td>
                  <td className="py-4 px-6 text-emerald-300 font-bold flex items-center gap-2">
                    <CheckCircle2 className="w-4 h-4 text-emerald-400" /> 0.001s (Instant)
                  </td>
                  <td className="py-4 px-6 text-rose-400">1.5 - 2.0s delay</td>
                  <td className="py-4 px-6 text-amber-400">0.8 - 1.2s delay</td>
                </tr>
                <tr className="hover:bg-slate-800/30 transition-colors">
                  <td className="py-4 px-6 font-medium">Preedit Chrome / Space Deletion</td>
                  <td className="py-4 px-6 text-emerald-300 font-bold flex items-center gap-2">
                    <CheckCircle2 className="w-4 h-4 text-emerald-400" /> Fixed & Safe
                  </td>
                  <td className="py-4 px-6 text-rose-400">Frequently erases word</td>
                  <td className="py-4 px-6 text-rose-400">Composition breaks</td>
                </tr>
                <tr className="hover:bg-slate-800/30 transition-colors">
                  <td className="py-4 px-6 font-medium">Dictionary Size</td>
                  <td className="py-4 px-6 text-emerald-300 font-bold flex items-center gap-2">
                    <CheckCircle2 className="w-4 h-4 text-emerald-400" /> 177,000+ Words
                  </td>
                  <td className="py-4 px-6 text-slate-400">~60,000 Words</td>
                  <td className="py-4 px-6 text-slate-400">~25,000 Words</td>
                </tr>
                <tr className="hover:bg-slate-800/30 transition-colors">
                  <td className="py-4 px-6 font-medium">NumPad Arithmetic & Numbers</td>
                  <td className="py-4 px-6 text-emerald-300 font-bold flex items-center gap-2">
                    <CheckCircle2 className="w-4 h-4 text-emerald-400" /> Full Native Support
                  </td>
                  <td className="py-4 px-6 text-rose-400">Outputs Halfwidth garbage</td>
                  <td className="py-4 px-6 text-amber-400">Partial / Breaks</td>
                </tr>
                <tr className="hover:bg-slate-800/30 transition-colors">
                  <td className="py-4 px-6 font-medium">Direct Digit Typing</td>
                  <td className="py-4 px-6 text-emerald-300 font-bold flex items-center gap-2">
                    <CheckCircle2 className="w-4 h-4 text-emerald-400" /> Direct (No Candidate Hijack)
                  </td>
                  <td className="py-4 px-6 text-rose-400">Hijacks candidate #1-#9</td>
                  <td className="py-4 px-6 text-slate-400">Intermittent</td>
                </tr>
                <tr className="hover:bg-slate-800/30 transition-colors">
                  <td className="py-4 px-6 font-medium">Wayland Support</td>
                  <td className="py-4 px-6 text-emerald-300 font-bold flex items-center gap-2">
                    <CheckCircle2 className="w-4 h-4 text-emerald-400" /> Full Native Wayland
                  </td>
                  <td className="py-4 px-6 text-amber-400">Prone to IBus crashes</td>
                  <td className="py-4 px-6 text-slate-400">Untested / Flaky</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </section>

      {/* Phonetic Cheat Sheet Section */}
      <section id="cheatsheet" className="py-20 sm:py-24 border-t border-white/5">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center max-w-2xl mx-auto mb-14">
            <h2 className="text-xs sm:text-sm font-bold uppercase tracking-widest text-emerald-400 mb-3">Typing Reference</h2>
            <p className="text-3xl sm:text-4xl font-extrabold text-white tracking-tight">
              Intuitive Avro Phonetic Mapping
            </p>
            <p className="mt-4 text-slate-400 text-base">
              Natural phonetic mappings designed for the fastest muscle memory without looking at reference sheets.
            </p>
          </div>

          <div className="flex justify-center mb-8">
            <div className="glass-panel p-1.5 rounded-xl flex gap-1 text-xs sm:text-sm font-medium overflow-x-auto max-w-full">
              {[
                { id: "vowels", label: "Vowels (Shoroborno)" },
                { id: "consonants", label: "Consonants (Benjonborno)" },
                { id: "modifiers", label: "Modifiers & Punctuation" },
                { id: "numbers", label: "Numbers" }
              ].map(tab => (
                <button
                  key={tab.id}
                  onClick={() => setCheatTab(tab.id)}
                  className={`px-3.5 py-2 rounded-lg transition-all whitespace-nowrap ${
                    cheatTab === tab.id 
                      ? "bg-emerald-500 text-slate-950 font-bold shadow-md shadow-emerald-500/20" 
                      : "text-slate-400 hover:text-white"
                  }`}
                >
                  {tab.label}
                </button>
              ))}
            </div>
          </div>

          <div className="glass-card rounded-2xl p-6 sm:p-8 max-w-4xl mx-auto border border-white/10">
            {cheatTab === "vowels" && (
              <div className="grid grid-cols-2 sm:grid-cols-4 md:grid-cols-5 gap-4">
                {[
                  { key: "o / a", bn: "অ / আ" },
                  { key: "i", bn: "ই / ি" },
                  { key: "I / ee", bn: "ঈ / ী" },
                  { key: "u", bn: "উ / ু" },
                  { key: "U / oo", bn: "ঊ / ূ" },
                  { key: "r", bn: "ঋ / ৃ" },
                  { key: "e", bn: "এ / ে" },
                  { key: "OI", bn: "ঐ / ৈ" },
                  { key: "O", bn: "ও / ো" },
                  { key: "OU", bn: "ঔ / ৌ" }
                ].map((item, idx) => (
                  <div key={idx} className="p-3.5 rounded-xl bg-slate-900/80 border border-slate-800 text-center">
                    <span className="font-mono text-emerald-400 font-bold text-sm block mb-1">{item.key}</span>
                    <span className="font-bengali text-xl font-semibold text-white">{item.bn}</span>
                  </div>
                ))}
              </div>
            )}

            {cheatTab === "consonants" && (
              <div className="grid grid-cols-2 sm:grid-cols-4 md:grid-cols-6 gap-3">
                {[
                  { key: "k", bn: "ক" }, { key: "kh", bn: "খ" }, { key: "g", bn: "গ" }, { key: "gh", bn: "ঘ" }, { key: "Ng", bn: "ঙ" },
                  { key: "c", bn: "চ" }, { key: "ch", bn: "ছ" }, { key: "j", bn: "জ" }, { key: "jh", bn: "ঝ" }, { key: "NG", bn: "ঞ" },
                  { key: "T", bn: "ট" }, { key: "Th", bn: "ঠ" }, { key: "D", bn: "ড" }, { key: "Dh", bn: "ঢ" }, { key: "N", bn: "ণ" },
                  { key: "t", bn: "ত" }, { key: "th", bn: "থ" }, { key: "d", bn: "দ" }, { key: "dh", bn: "ধ" }, { key: "n", bn: "ন" },
                  { key: "p", bn: "প" }, { key: "ph / f", bn: "ফ" }, { key: "b", bn: "ব" }, { key: "bh / v", bn: "ভ" }, { key: "m", bn: "ম" },
                  { key: "z / j", bn: "য" }, { key: "r", bn: "র" }, { key: "l", bn: "ল" }, { key: "sh", bn: "শ" }, { key: "S / Sh", bn: "ষ" },
                  { key: "s", bn: "স" }, { key: "h", bn: "হ" }, { key: "R", bn: "ড়" }, { key: "Rh", bn: "ঢ়" }, { key: "y", bn: "য়" }
                ].map((item, idx) => (
                  <div key={idx} className="p-3 rounded-xl bg-slate-900/80 border border-slate-800 text-center">
                    <span className="font-mono text-cyan-400 font-bold text-xs block mb-1">{item.key}</span>
                    <span className="font-bengali text-xl font-semibold text-white">{item.bn}</span>
                  </div>
                ))}
              </div>
            )}

            {cheatTab === "modifiers" && (
              <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-4">
                {[
                  { key: ": (colon)", bn: "ঃ (Bisarga)", desc: "Type du:kho -> দুঃখ" },
                  { key: ",, (double comma)", bn: "্ (Hasanta)", desc: "Type k,, -> ক্‌" },
                  { key: ". (period)", bn: "। (Dari)", desc: "Type . -> ।" },
                  { key: "$ (dollar)", bn: "৳ (Taka)", desc: "Type $ -> ৳" },
                  { key: "^ (caret)", bn: "ঁ (Chandrabindu)", desc: "Type ca^d -> চাঁদ" },
                  { key: "` (backtick)", bn: "Literal `", desc: "Break conjunct or code" }
                ].map((item, idx) => (
                  <div key={idx} className="p-4 rounded-xl bg-slate-900/80 border border-slate-800">
                    <div className="flex items-center justify-between mb-1">
                      <span className="font-mono text-emerald-400 font-bold text-xs">{item.key}</span>
                      <span className="font-bengali text-base font-semibold text-white">{item.bn}</span>
                    </div>
                    <p className="text-xs text-slate-400">{item.desc}</p>
                  </div>
                ))}
              </div>
            )}

            {cheatTab === "numbers" && (
              <div className="grid grid-cols-2 sm:grid-cols-5 gap-3">
                {[
                  { key: "0", bn: "০" }, { key: "1", bn: "১" }, { key: "2", bn: "২" }, { key: "3", bn: "৩" }, { key: "4", bn: "৪" },
                  { key: "5", bn: "৫" }, { key: "6", bn: "৬" }, { key: "7", bn: "৭" }, { key: "8", bn: "৮" }, { key: "9", bn: "৯" }
                ].map((item, idx) => (
                  <div key={idx} className="p-3.5 rounded-xl bg-slate-900/80 border border-slate-800 text-center">
                    <span className="font-mono text-emerald-400 font-bold text-sm block mb-1">{item.key}</span>
                    <span className="font-bengali text-2xl font-bold text-white">{item.bn}</span>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </section>

      {/* Installation Guide */}
      <section id="install" className="py-20 sm:py-24 bg-slate-900/40 border-t border-white/5">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-12">
            <h2 className="text-xs sm:text-sm font-bold uppercase tracking-widest text-emerald-400 mb-3">Get Started</h2>
            <p className="text-3xl sm:text-4xl font-extrabold text-white tracking-tight">
              Install BanglaFlow in Seconds
            </p>
            <p className="mt-3 text-slate-400 text-base">
              Choose your preferred distribution package below.
            </p>
          </div>

          {/* Installation Method Tabs */}
          <div className="flex justify-center mb-8">
            <div className="glass-panel p-1.5 rounded-xl flex gap-1 text-sm font-medium overflow-x-auto max-w-full">
              <button
                onClick={() => setInstallTab("deb")}
                className={`px-5 py-2.5 rounded-lg flex items-center gap-2 transition-all whitespace-nowrap ${
                  installTab === "deb"
                    ? "bg-emerald-500 text-slate-950 font-bold shadow-md shadow-emerald-500/20"
                    : "text-slate-400 hover:text-white"
                }`}
              >
                <Download className="w-4 h-4" />
                <span>Debian Package (.deb)</span>
              </button>
              <button
                id="snap-install"
                onClick={() => setInstallTab("snap")}
                className={`px-5 py-2.5 rounded-lg flex items-center gap-2 transition-all whitespace-nowrap ${
                  installTab === "snap"
                    ? "bg-cyan-500 text-slate-950 font-bold shadow-md shadow-cyan-500/20"
                    : "text-slate-400 hover:text-white"
                }`}
              >
                <Terminal className="w-4 h-4" />
                <span>Snap Store</span>
              </button>
              <button
                onClick={() => setInstallTab("source")}
                className={`px-5 py-2.5 rounded-lg flex items-center gap-2 transition-all whitespace-nowrap ${
                  installTab === "source"
                    ? "bg-teal-500 text-slate-950 font-bold shadow-md shadow-teal-500/20"
                    : "text-slate-400 hover:text-white"
                }`}
              >
                <Layers className="w-4 h-4" />
                <span>Build from Source</span>
              </button>
            </div>
          </div>

          {/* Tab 1: DEB */}
          {installTab === "deb" && (
            <div className="glass-panel rounded-2xl p-6 sm:p-8 border border-white/10 shadow-xl space-y-6">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between pb-4 border-b border-white/5 gap-4">
                <div>
                  <div className="flex items-center gap-2">
                    <h3 className="text-lg font-bold text-white">Recommended for Ubuntu / Debian</h3>
                    <span className="px-2 py-0.5 text-[11px] font-semibold bg-emerald-500/20 text-emerald-400 rounded-full border border-emerald-500/30">
                      {releaseInfo.version}
                    </span>
                  </div>
                  <p className="text-xs text-slate-400 mt-0.5">One-click installation for Ubuntu 24.04 / 26.04 LTS.</p>
                </div>
                <a 
                  href={releaseInfo.debUrl}
                  download
                  className="px-4 py-2.5 rounded-xl bg-emerald-500 hover:bg-emerald-400 text-slate-950 font-bold text-xs flex items-center justify-center gap-1.5 transition-colors shadow-lg shadow-emerald-500/20 self-start sm:self-auto"
                >
                  <Download className="w-3.5 h-3.5" />
                  <span>Download {releaseInfo.debFileName}</span>
                </a>
              </div>

              <div>
                <span className="text-xs font-semibold text-slate-400 block mb-2">Step 1: Install the downloaded package</span>
                <div className="relative">
                  <pre className="p-4 rounded-xl bg-slate-900 border border-slate-800 text-emerald-400 font-mono text-sm overflow-x-auto">
                    <code>sudo dpkg -i {releaseInfo.debFileName}{'\n'}sudo apt-get install -f</code>
                  </pre>
                  <button 
                    onClick={() => copyToClipboard(`sudo dpkg -i ${releaseInfo.debFileName}\nsudo apt-get install -f`, 'deb-cmd')}
                    className="absolute right-3 top-3 p-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 transition-colors"
                    title="Copy command"
                  >
                    {copiedCmd === 'deb-cmd' ? <Check className="w-4 h-4 text-emerald-400" /> : <Copy className="w-4 h-4" />}
                  </button>
                </div>
              </div>

              <div>
                <span className="text-xs font-semibold text-slate-400 block mb-2">Step 2: Restart IBus</span>
                <div className="relative">
                  <pre className="p-4 rounded-xl bg-slate-900 border border-slate-800 text-emerald-400 font-mono text-sm overflow-x-auto">
                    <code>ibus restart</code>
                  </pre>
                  <button 
                    onClick={() => copyToClipboard('ibus restart', 'ibus-cmd')}
                    className="absolute right-3 top-3 p-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 transition-colors"
                  >
                    {copiedCmd === 'ibus-cmd' ? <Check className="w-4 h-4 text-emerald-400" /> : <Copy className="w-4 h-4" />}
                  </button>
                </div>
              </div>

              <div>
                <span className="text-xs font-semibold text-slate-400 block mb-2">Step 3: Enable in GNOME Settings</span>
                <p className="text-xs text-slate-300 bg-slate-900/60 p-4 rounded-xl border border-slate-800 leading-relaxed">
                  Open <strong>Settings</strong> → <strong>Keyboard</strong> → <strong>Input Sources</strong> → Click <strong>Add (+)</strong> → Select <strong>Bengali</strong> → Choose <strong>BanglaFlow</strong>.
                </p>
              </div>
            </div>
          )}

          {/* Tab 2: SNAP */}
          {installTab === "snap" && (
            <div className="glass-panel rounded-2xl p-6 sm:p-8 border border-white/10 shadow-xl space-y-6">
              <div>
                <div className="flex items-center gap-2">
                  <h3 className="text-lg font-bold text-white">Install from Canonical Snap Store</h3>
                  <span className="px-2 py-0.5 text-[11px] font-semibold bg-cyan-500/20 text-cyan-400 rounded-full border border-cyan-500/30">
                    Universal Snap
                  </span>
                </div>
                <p className="text-xs text-slate-400 mt-0.5">Compatible across Ubuntu, Debian, Fedora, Arch, and all snap-enabled distributions.</p>
              </div>

              <div>
                <span className="text-xs font-semibold text-slate-400 block mb-2">Terminal Command (Install & Restart IBus):</span>
                <div className="relative">
                  <pre className="p-4 rounded-xl bg-slate-900 border border-slate-800 text-cyan-400 font-mono text-sm overflow-x-auto">
                    <code>sudo snap install --classic banglaflow{'\n'}ibus restart</code>
                  </pre>
                  <button 
                    onClick={() => copyToClipboard('sudo snap install --classic banglaflow\nibus restart', 'snap-cmd')}
                    className="absolute right-3 top-3 p-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 transition-colors"
                    title="Copy snap installation & restart command"
                  >
                    {copiedCmd === 'snap-cmd' ? <Check className="w-4 h-4 text-emerald-400" /> : <Copy className="w-4 h-4" />}
                  </button>
                </div>
              </div>

              <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800 space-y-2 text-xs text-slate-300">
                <div className="flex items-start gap-2">
                  <span className="w-5 h-5 rounded-full bg-cyan-500/20 text-cyan-300 font-bold flex items-center justify-center flex-shrink-0 text-[11px]">1</span>
                  <p>Installs the isolated, auto-updating <strong>banglaflow</strong> snap package with classic system integration.</p>
                </div>
                <div className="flex items-start gap-2">
                  <span className="w-5 h-5 rounded-full bg-cyan-500/20 text-cyan-300 font-bold flex items-center justify-center flex-shrink-0 text-[11px]">2</span>
                  <p>Running <code className="text-emerald-400 font-mono bg-slate-800 px-1.5 py-0.5 rounded">ibus restart</code> immediately registers the new engine into your desktop session without a reboot.</p>
                </div>
                <div className="flex items-start gap-2">
                  <span className="w-5 h-5 rounded-full bg-cyan-500/20 text-cyan-300 font-bold flex items-center justify-center flex-shrink-0 text-[11px]">3</span>
                  <p>Activate via <strong>Settings</strong> → <strong>Keyboard</strong> → <strong>Add (+)</strong> → <strong>Bengali (BanglaFlow)</strong>.</p>
                </div>
              </div>
            </div>
          )}

          {/* Tab 3: SOURCE */}
          {installTab === "source" && (
            <div className="glass-panel rounded-2xl p-6 sm:p-8 border border-white/10 shadow-xl space-y-6">
              <div>
                <h3 className="text-lg font-bold text-white mb-1">Build & Install from Git</h3>
                <p className="text-xs text-slate-400">Compile and verify directly from the open source repository.</p>
              </div>

              <div className="relative">
                <pre className="p-4 rounded-xl bg-slate-900 border border-slate-800 text-teal-400 font-mono text-sm overflow-x-auto">
                  <code>git clone https://github.com/{GITHUB_REPO}.git{'\n'}cd BanglaFlow-Bangla-Phonetic-Keyboard-for-linux{'\n'}bash scripts/build-deb.sh{'\n'}sudo dpkg -i banglaflow.deb{'\n'}ibus restart</code>
                </pre>
                <button 
                  onClick={() => copyToClipboard(`git clone https://github.com/${GITHUB_REPO}.git\ncd BanglaFlow-Bangla-Phonetic-Keyboard-for-linux\nbash scripts/build-deb.sh\nsudo dpkg -i banglaflow.deb\nibus restart`, 'source-cmd')}
                  className="absolute right-3 top-3 p-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 transition-colors"
                >
                  {copiedCmd === 'source-cmd' ? <Check className="w-4 h-4 text-emerald-400" /> : <Copy className="w-4 h-4" />}
                </button>
              </div>
            </div>
          )}
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-white/5 py-12 glass-panel">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex flex-col sm:flex-row items-center justify-between gap-6">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-lg bg-gradient-to-tr from-emerald-500 to-cyan-500 p-0.5">
              <img src="./logo.png" alt="BanglaFlow" className="w-full h-full object-cover rounded-[6px]" />
            </div>
            <div>
              <span className="font-bold text-white">BanglaFlow</span>
              <p className="text-xs text-slate-400">Developed by <a href="https://kovence.com" target="_blank" rel="noreferrer" className="text-emerald-400 hover:underline">Kovence</a></p>
            </div>
          </div>

          <div className="flex items-center gap-6 text-xs text-slate-400">
            <span>Licensed under <strong className="text-slate-300">GNU GPL-3.0</strong></span>
            <span>•</span>
            <a 
              href={`https://github.com/${GITHUB_REPO}`} 
              target="_blank" 
              rel="noreferrer" 
              className="text-slate-300 hover:text-white transition-colors flex items-center gap-1"
            >
              GitHub Repository <ExternalLink className="w-3 h-3" />
            </a>
          </div>
        </div>
      </footer>
    </div>
  );
}
