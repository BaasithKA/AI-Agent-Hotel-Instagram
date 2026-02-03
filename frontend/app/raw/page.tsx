"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { ArrowLeft, Database, Search, RefreshCw } from "lucide-react";

export default function RawDataPage() {
  const [hotels, setHotels] = useState<any[]>([]);
  const [searchTerm, setSearchTerm] = useState("");
  const [loading, setLoading] = useState(true);

  const fetchRawData = async () => {
    setLoading(true);
    try {
      const res = await fetch("http://127.0.0.1:8000/api/hotels/raw");
      const data = await res.json();
      setHotels(data);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchRawData();
  }, []);

  const filteredHotels = hotels.filter(
    (h) =>
      h.hotel_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      h.location.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <main className="min-h-screen bg-[#050505] text-slate-300 p-8 font-mono">
      <div className="max-w-7xl mx-auto space-y-6">
        <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
          <Link
            href="/"
            className="flex items-center gap-2 text-blue-500 hover:text-blue-400 transition-all font-bold"
          >
            <ArrowLeft size={18} /> KEMBALI KE DASHBOARD
          </Link>

          <div className="flex items-center gap-3 w-full md:w-auto">
            <div className="flex items-center gap-2 bg-slate-900 px-4 py-2 rounded-lg border border-slate-800 flex-1">
              <Search size={16} className="text-slate-500" />
              <input
                type="text"
                placeholder="Cari nama hotel atau lokasi..."
                className="bg-transparent outline-none text-sm w-full"
                onChange={(e) => setSearchTerm(e.target.value)}
              />
            </div>
            <button
              onClick={fetchRawData}
              className="p-2 bg-slate-900 border border-slate-800 rounded-lg hover:bg-slate-800 text-blue-500"
            >
              <RefreshCw size={20} className={loading ? "animate-spin" : ""} />
            </button>
          </div>
        </div>

        <div className="flex items-center gap-3 border-b border-slate-800 pb-4">
          <Database className="text-blue-500" size={24} />
          <div>
            <h1 className="text-xl font-bold text-white uppercase tracking-tighter text-blue-500">
              Raw Database Explorer
            </h1>
            <p className="text-[10px] text-slate-500 uppercase">
              Tampilan Langsung Data Tabel: public.hotel
            </p>
          </div>
          <div className="ml-auto text-xs bg-blue-900/20 text-blue-400 px-3 py-1 rounded border border-blue-800">
            {filteredHotels.length} Records
          </div>
        </div>

        <div className="bg-slate-950 rounded-xl border border-slate-800 overflow-hidden shadow-2xl">
          <div className="overflow-x-auto">
            <table className="w-full text-left text-[11px] border-collapse">
              <thead>
                <tr className="bg-slate-900 text-slate-500 uppercase border-b border-slate-800">
                  <th className="p-4 font-bold">ID</th>
                  <th className="p-4 font-bold">Hotel Info</th>
                  <th className="p-4 font-bold">Price Metrics</th>
                  <th className="p-4 font-bold">Rating & Reviews</th>
                  <th className="p-4 font-bold">Amenities Snippet</th>
                  <th className="p-4 font-bold">AI Status</th>
                  <th className="p-4 font-bold">Timestamp</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-900">
                {filteredHotels.length > 0 ? (
                  filteredHotels.map((hotel) => (
                    <tr
                      key={hotel.id}
                      className="hover:bg-blue-900/5 transition-colors border-b border-slate-900/50"
                    >
                      <td className="p-4 text-slate-600 font-mono">
                        #{hotel.id}
                      </td>
                      <td className="p-4">
                        <div className="text-blue-400 font-bold mb-1 uppercase">
                          {hotel.hotel_name}
                        </div>
                        <div className="text-slate-500 italic">
                          {hotel.location}
                        </div>
                      </td>
                      <td className="p-4">
                        <div className="text-green-500 font-bold">
                          {hotel.discounted_price || "N/A"}
                        </div>
                        <div className="text-slate-600 line-through text-[9px]">
                          {hotel.original_price}
                        </div>
                        {hotel.deal_badge && (
                          <span className="text-[8px] bg-red-900/20 text-red-400 px-1 rounded uppercase mt-1 block w-fit">
                            {hotel.deal_badge}
                          </span>
                        )}
                      </td>
                      <td className="p-4">
                        <div className="text-slate-200">
                          {hotel.rating} / 10
                        </div>
                        <div className="text-slate-500 text-[9px] mb-1">
                          {hotel.rating_text}
                        </div>
                        <div className="text-slate-600 text-[9px] italic">
                          {hotel.review_count} reviews
                        </div>
                      </td>
                      <td className="p-4 max-w-[200px]">
                        <div
                          className="truncate text-slate-500"
                          title={hotel.amenities}
                        >
                          {hotel.amenities || "No amenities listed"}
                        </div>
                      </td>
                      <td className="p-4">
                        <span
                          className={`px-2 py-0.5 rounded text-[9px] font-bold ${
                            hotel.is_processed
                              ? "bg-green-900/20 text-green-500 border border-green-800"
                              : "bg-yellow-900/20 text-yellow-500 border border-yellow-800"
                          }`}
                        >
                          {hotel.is_processed ? "PROCESSED" : "PENDING"}
                        </span>
                      </td>
                      <td className="p-4 text-slate-600 text-[10px]">
                        {new Date(hotel.created_at).toLocaleString("id-ID")}
                      </td>
                    </tr>
                  ))
                ) : (
                  <tr>
                    <td
                      colSpan={7}
                      className="p-20 text-center text-slate-600 uppercase tracking-widest"
                    >
                      {loading
                        ? "Menghubungkan ke Database..."
                        : "Data Tidak Ditemukan"}
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </div>

        <div className="flex justify-between items-center text-[10px] text-slate-700 uppercase tracking-widest px-2">
          <p>System: AI Hotel Agent v1.0</p>
          <p>Connection: PostgreSQL 127.0.0.1:5432</p>
        </div>
      </div>
    </main>
  );
}
