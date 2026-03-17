import React, { useState } from 'react';
import { Plus, Loader2 } from 'lucide-react';

export default function AddProductForm({ onAdd }) {
  const [url, setUrl] = useState('');
  const [price, setPrice] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    
    if (!url.includes('amazon')) {
      setError('Please enter a valid Amazon URL.');
      return;
    }
    if (!price || isNaN(price) || Number(price) <= 0) {
      setError('Please enter a valid target price.');
      return;
    }

    setLoading(true);
    try {
      // Assuming we're directly calling our local FastAPI server set up on port 8000
      const response = await fetch('/api/track', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          url: url,
          target_price: Number(price)
        }),
      });

      const data = await response.json();
      
      if (!response.ok || !data.success) {
        throw new Error(data.detail || data.message || 'Failed to add product');
      }

      // Reset form on success
      setUrl('');
      setPrice('');
      if (onAdd) onAdd(); // Tell dashboard to refresh
      
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-surface p-6 rounded-lg border border-neutral-800 shadow-2xl">
      <h2 className="text-xl font-semibold text-textPrimary mb-4">Track New Product</h2>
      
      <form onSubmit={handleSubmit} className="flex flex-col md:flex-row gap-4">
        <div className="flex-1 text-left">
          <label className="block text-xs uppercase text-textSecondary tracking-wider mb-2 font-semibold">Url</label>
          <input 
            type="text" 
            placeholder="https://www.amazon.in/dp/..." 
            className="w-full bg-[#0D0D0D] border border-neutral-800 rounded-md px-4 py-3 text-sm focus:outline-none focus:border-accent text-textPrimary placeholder-neutral-600 transition-colors"
            value={url}
            onChange={(e) => setUrl(e.target.value)}
            disabled={loading}
          />
        </div>
        
        <div className="md:w-48 text-left">
          <label className="block text-xs uppercase text-textSecondary tracking-wider mb-2 font-semibold">Target Price</label>
          <div className="relative">
            <span className="absolute left-4 top-1/2 -translate-y-1/2 text-neutral-500 font-medium">₹</span>
            <input 
              type="number" 
              placeholder="599.00" 
              className="w-full bg-[#0D0D0D] border border-neutral-800 rounded-md pl-8 pr-4 py-3 text-sm focus:outline-none focus:border-accent text-textPrimary placeholder-neutral-600 transition-colors"
              value={price}
              onChange={(e) => setPrice(e.target.value)}
              disabled={loading}
            />
          </div>
        </div>
        
        <div className="flex items-end">
          <button 
            type="submit" 
            disabled={loading}
            className="w-full md:w-auto h-[46px] px-6 bg-accent hover:bg-[#E55F00] text-black font-semibold rounded-md transition-colors flex items-center justify-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {loading ? <Loader2 className="w-5 h-5 animate-spin" /> : <Plus className="w-5 h-5" />}
            {loading ? 'Adding...' : 'Track'}
          </button>
        </div>
      </form>
      
      {error && (
        <div className="mt-4 p-3 bg-red-950/30 border border-red-900/50 rounded-md text-red-400 text-sm">
          {error}
        </div>
      )}
    </div>
  );
}
