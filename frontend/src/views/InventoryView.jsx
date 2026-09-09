import React, { useState, useEffect } from 'react';
import { 
  Package, 
  CheckCircle2, 
  AlertTriangle, 
  Search, 
  Tag, 
  DollarSign, 
  Truck 
} from 'lucide-react';

export default function InventoryView() {
  const [parts, setParts] = useState([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchParts = async () => {
      try {
        const res = await fetch('/api/inventory/parts');
        if (res.ok) setParts(await res.json());
      } catch (e) {
        console.error("Fetch parts error:", e);
      } finally {
        setLoading(false);
      }
    };
    fetchParts();
  }, []);

  const filteredParts = parts.filter(p => 
    p.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    p.part_number.toLowerCase().includes(searchTerm.toLowerCase()) ||
    p.compatible_machine.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div className="space-y-6">
      {/* Header Bar */}
      <div className="glass-card p-6 rounded-2xl flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
        <div>
          <div className="flex items-center gap-2">
            <Package className="w-6 h-6 text-amber-400" />
            <h2 className="text-xl md:text-2xl font-extrabold text-white">Industrial Spare Parts Inventory</h2>
          </div>
          <p className="text-xs text-slate-400 mt-1 font-mono">Catalog of replacement components, stock availability, pricing, and supplier reorder routing.</p>
        </div>

        {/* Search Bar */}
        <div className="relative w-full md:w-72">
          <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            placeholder="Search part name, #no, machine..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full bg-slate-900 border border-slate-700 text-slate-200 text-xs rounded-xl pl-9 pr-4 py-2 outline-none focus:border-cyan-500 font-mono"
          />
        </div>
      </div>

      {/* Parts Inventory Table Card */}
      <div className="glass-card p-6 rounded-2xl space-y-4">
        {loading ? (
          <div className="p-8 text-center text-slate-400 font-mono animate-pulse">Loading spare parts catalog...</div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs font-mono">
              <thead className="bg-slate-900/80 text-slate-400 border-b border-slate-800 uppercase tracking-wider">
                <tr>
                  <th className="p-3">Part Number</th>
                  <th className="p-3">Part Name</th>
                  <th className="p-3">Machine Line</th>
                  <th className="p-3">Manufacturer</th>
                  <th className="p-3">Stock State</th>
                  <th className="p-3">Unit Price</th>
                  <th className="p-3">Lead Time</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60 text-slate-300">
                {filteredParts.map((p) => (
                  <tr key={p.part_number} className="hover:bg-slate-800/40 transition">
                    <td className="p-3 font-bold text-cyan-400">{p.part_number}</td>
                    <td className="p-3 font-bold text-slate-200">{p.name}</td>
                    <td className="p-3">
                      <span className="px-2 py-0.5 rounded bg-slate-800 text-slate-300 font-bold uppercase">
                        {p.compatible_machine}
                      </span>
                    </td>
                    <td className="p-3 text-slate-400">{p.manufacturer}</td>
                    <td className="p-3">
                      {p.stock_qty > 0 ? (
                        <span className="px-2.5 py-0.5 rounded-full font-bold text-[10px] bg-emerald-500/20 text-emerald-400 border border-emerald-500/30">
                          {p.stock_qty} IN STOCK
                        </span>
                      ) : (
                        <span className="px-2.5 py-0.5 rounded-full font-bold text-[10px] bg-rose-500/20 text-rose-400 border border-rose-500/30 animate-pulse">
                          OUT OF STOCK
                        </span>
                      )}
                    </td>
                    <td className="p-3 text-emerald-400 font-bold">${p.unit_price}</td>
                    <td className="p-3 text-slate-400">{p.lead_time_days} Days</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
