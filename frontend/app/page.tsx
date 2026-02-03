"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import {
  Search,
  Sparkles,
  Terminal,
  RefreshCw,
  TableProperties,
  Loader2,
  CheckCircle,
  Instagram,
  Play,
  Square,
  Clock,
} from "lucide-react";

interface Post {
  post_id: number;
  hotel_name: string;
  image_url: string;
  caption: string;
  hashtags: string;
  status: string;
}

export default function Dashboard() {
  const [location, setLocation] = useState("");
  const [posts, setPosts] = useState<Post[]>([]);
  const [logs, setLogs] = useState<string[]>([]);
  const [loading, setLoading] = useState({
    scrape: false,
    gen: false,
    publishing: 0,
  });
  const [isBotRunning, setIsBotRunning] = useState(false);
  const [botInterval, setBotInterval] = useState(60);

  const API_URL = "http://127.0.0.1:8000/api";

  useEffect(() => {
    const fetchData = async () => {
      try {
        const logRes = await fetch(`${API_URL}/logs`);
        if (logRes.ok) {
          setLogs(await logRes.json());
        }

        const statusRes = await fetch(`${API_URL}/bot/status`);
        if (statusRes.ok) {
          const statusData = await statusRes.json();
          setIsBotRunning(statusData.is_running);
        }
      } catch {}
    };

    fetchData();
    const intervalId = setInterval(fetchData, 2000);
    return () => clearInterval(intervalId);
  }, []);

  const fetchPosts = async () => {
    try {
      const res = await fetch(`${API_URL}/posts`);
      if (res.ok) setPosts(await res.json());
    } catch {}
  };

  useEffect(() => {
    fetchPosts();
  }, []);

  const toggleBot = async () => {
    const endpoint = isBotRunning ? "stop" : "start";

    if (!isBotRunning && botInterval < 1) {
      alert("Minimal interval 1 menit!");
      return;
    }

    try {
      const url =
        endpoint === "start"
          ? `${API_URL}/bot/start?minutes=${botInterval}`
          : `${API_URL}/bot/stop`;

      const res = await fetch(url, { method: "POST" });
      const data = await res.json();

      if (data.status === "success") {
        setIsBotRunning(!isBotRunning);
        setTimeout(async () => {
          const logRes = await fetch(`${API_URL}/logs`);
          if (logRes.ok) setLogs(await logRes.json());
        }, 500);
      } else {
        alert(data.message);
      }
    } catch {
      alert("Gagal menghubungi server. Pastikan Backend nyala!");
    }
  };

  const handleScrape = async () => {
    if (!location) {
      alert("Isi lokasi dulu!");
      return;
    }

    setLoading((p) => ({ ...p, scrape: true }));

    try {
      const res = await fetch(`${API_URL}/scrape`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ location }),
      });
      if (res.ok) fetchPosts();
    } finally {
      setLoading((p) => ({ ...p, scrape: false }));
    }
  };

  const handleGenerate = async () => {
    setLoading((p) => ({ ...p, gen: true }));

    try {
      const res = await fetch(`${API_URL}/generate-content`, {
        method: "POST",
      });
      if (res.ok) fetchPosts();
    } finally {
      setLoading((p) => ({ ...p, gen: false }));
    }
  };

  const handlePublish = async (postId: number) => {
    setLoading((p) => ({ ...p, publishing: postId }));

    try {
      const res = await fetch(`${API_URL}/posts/${postId}/publish`, {
        method: "POST",
      });
      if (res.ok) fetchPosts();
    } finally {
      setLoading((p) => ({ ...p, publishing: 0 }));
    }
  };

  return (
    <main className="min-h-screen bg-[#0a0a0c] text-slate-200 p-6 md:p-12 font-sans">
      <div className="max-w-7xl mx-auto space-y-8">
        <div className="flex flex-col xl:flex-row justify-between items-start xl:items-end border-b border-slate-800 pb-6 gap-6">
          <div>
            <h1 className="text-4xl font-extrabold text-white tracking-tighter uppercase">
              AI Agent <span className="text-blue-500">Manager</span>
            </h1>
            <p className="text-slate-500 mt-2 font-medium">
              Expedia Scraper & Instagram Automation
            </p>
          </div>

          <div className="flex gap-3 bg-slate-900/50 p-2 rounded-2xl border border-slate-800">
            <div className="flex items-center gap-2 px-3 py-2 bg-slate-950 rounded-xl border border-slate-800">
              <Clock size={16} className="text-slate-400" />
              <input
                type="number"
                min="1"
                value={botInterval}
                onChange={(e) => setBotInterval(Number(e.target.value))}
                disabled={isBotRunning}
                className="bg-transparent w-12 text-center outline-none font-bold text-white disabled:opacity-50"
              />
              <span className="text-xs text-slate-500 font-bold">MENIT</span>
            </div>

            <button
              onClick={toggleBot}
              className={`px-4 py-2 rounded-xl font-bold text-sm flex items-center gap-2 transition-all shadow-lg ${
                isBotRunning
                  ? "bg-red-500/10 text-red-500 border border-red-500/50 hover:bg-red-500 hover:text-white"
                  : "bg-green-500/10 text-green-500 border border-green-500/50 hover:bg-green-500 hover:text-white"
              }`}
            >
              {isBotRunning ? (
                <>
                  <Square size={16} fill="currentColor" /> STOP BOT
                </>
              ) : (
                <>
                  <Play size={16} fill="currentColor" /> START BOT
                </>
              )}
            </button>

            <div className="w-[1px] bg-slate-800 mx-1"></div>

            <Link
              href="/raw"
              className="flex items-center gap-2 bg-slate-900 px-4 py-2 rounded-xl border border-slate-800 text-sm font-bold text-slate-400 hover:text-white transition-all"
            >
              <TableProperties size={16} className="text-blue-500" /> DB VIEW
            </Link>
          </div>
        </div>

        <div className="bg-[#050505] p-5 rounded-3xl border border-slate-800 font-mono text-xs h-64 overflow-y-auto shadow-2xl">
          <div className="flex justify-between text-slate-500 mb-4 border-b border-slate-800 pb-2 sticky top-0 bg-[#050505] z-10">
            <span className="flex items-center gap-2 font-bold tracking-widest text-slate-300">
              <Terminal size={14} className="text-green-500" /> SYSTEM_LOGS
            </span>
            {isBotRunning && (
              <span className="flex items-center gap-1.5 text-green-500 text-[10px] font-bold animate-pulse">
                <div className="h-1.5 w-1.5 rounded-full bg-green-500"></div>
                LIVE
              </span>
            )}
          </div>

          <div className="space-y-1.5 flex flex-col">
            {logs.length === 0 && (
              <div className="text-slate-700 italic text-center mt-10">
                ... Menunggu aktivitas ...
              </div>
            )}
            {logs.map((log, i) => (
              <div
                key={i}
                className={`pb-1 border-b border-dashed border-slate-800/50 flex gap-3 p-1 rounded hover:bg-white/5 ${
                  log.includes("❌")
                    ? "text-red-400 font-bold bg-red-500/5 border-l-2 border-l-red-500 pl-2"
                    : log.includes("✅")
                    ? "text-green-400 font-bold border-l-2 border-l-green-500 pl-2"
                    : log.includes("🤖")
                    ? "text-cyan-400"
                    : log.includes("🧠")
                    ? "text-purple-400"
                    : log.includes("📤")
                    ? "text-yellow-400"
                    : "text-slate-400"
                }`}
              >
                <span className="text-slate-600 font-bold min-w-[60px]">
                  {log.substring(1, 9)}
                </span>
                <span className="flex-1">{log.substring(11)}</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </main>
  );
}
