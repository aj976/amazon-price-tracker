import React from 'react';
import { ArrowDown, ArrowUp, Minus, ExternalLink, Trash2 } from 'lucide-react';

export default function ProductCard({ item, onRemove }) {
  const product = item.products || {};
  const currentPrice = product.latest_price || item.last_notified_price || 0; 
  const targetPrice = item.target_price;
  
  // Logic for the visual indicator
  let statusColor = "text-textSecondary";
  let StatusIcon = Minus;
  
  if (currentPrice > 0) {
    if (currentPrice <= targetPrice) {
      statusColor = "text-drop";
      StatusIcon = ArrowDown;
    } else if (currentPrice > targetPrice) {
      statusColor = "text-increase";
      StatusIcon = ArrowUp;
    }
  }

  const handleRemove = async () => {
    if (window.confirm(`Stop tracking ${product.title}?`)) {
      try {
        const res = await fetch(`/api/products/${product.asin}`, { method: 'DELETE' });
        if (res.ok) {
          onRemove();
        }
      } catch (err) {
        console.error("Failed to delete", err);
      }
    }
  };

  return (
    <div className="bg-surface rounded-lg border border-neutral-800 p-5 shadow-lg flex flex-col md:flex-row gap-6 relative group transition-all hover:border-neutral-700">
      
      {/* Visual Badge */}
      <div className={`hidden md:flex flex-col items-center justify-center p-4 rounded bg-[#0D0D0D] border border-neutral-800 min-w[80px] ${statusColor}`}>
         <StatusIcon className="w-8 h-8" />
      </div>

      <div className="flex-1 flex flex-col justify-between">
        <div>
          <div className="flex justify-between items-start gap-4">
            <h3 className="text-lg font-medium text-textPrimary leading-tight line-clamp-2">
              {product.title || "Unknown Product"}
            </h3>
            <button 
              onClick={handleRemove}
              className="text-neutral-600 hover:text-red-500 transition-colors bg-transparent border-0 opacity-0 group-hover:opacity-100"
              title="Remove Tracking"
            >
              <Trash2 className="w-5 h-5" />
            </button>
          </div>
          
          <div className="flex items-center gap-3 mt-2">
            <span className="text-xs font-mono text-neutral-500 bg-black px-2 py-1 rounded">
              ASIN: {product.asin}
            </span>
            <a 
              href={product.url} 
              target="_blank" 
              rel="noopener noreferrer"
              className="text-xs flex items-center gap-1 text-accent hover:underline"
            >
              View on Amazon <ExternalLink className="w-3 h-3" />
            </a>
          </div>
        </div>

        <div className="grid grid-cols-2 gap-4 mt-6">
          <div className="bg-[#0D0D0D] p-3 rounded border border-neutral-800">
            <p className="text-xs uppercase tracking-wider text-textSecondary font-semibold mb-1">Target Price</p>
            <p className="text-xl font-bold text-textPrimary">
              ₹{targetPrice?.toLocaleString('en-IN')}
            </p>
          </div>
          
          <div className="bg-[#0D0D0D] p-3 rounded border border-neutral-800">
             <p className="text-xs uppercase tracking-wider text-textSecondary font-semibold mb-1">Last Checked</p>
             <div className="flex items-center gap-2">
                <p className={`text-xl font-bold ${statusColor}`}>
                  {currentPrice > 0 ? `₹${currentPrice.toLocaleString('en-IN')}` : 'Pending...'}
                </p>
                <StatusIcon className={`w-4 h-4 md:hidden ${statusColor}`} />
             </div>
          </div>
        </div>
      </div>
    </div>
  );
}
