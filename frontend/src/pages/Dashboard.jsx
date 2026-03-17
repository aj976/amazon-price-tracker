import React, { useState, useEffect } from 'react';
import AddProductForm from '../components/AddProductForm';
import ProductCard from '../components/ProductCard';
import { RefreshCw } from 'lucide-react';

export default function Dashboard() {
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(true);

  const fetchItems = async () => {
    setLoading(true);
    try {
      const response = await fetch('/api/products');
      const result = await response.json();
      if (result.success) {
        setItems(result.data || []);
      }
    } catch (err) {
      console.error("Failed to fetch products:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchItems();
  }, []);

  return (
    <div className="flex flex-col gap-10">
      
      {/* Tracker Form */}
      <section>
        <AddProductForm onAdd={fetchItems} />
      </section>

      {/* Main List */}
      <section className="flex flex-col gap-4">
        <div className="flex items-center justify-between border-b border-neutral-800 pb-2">
          <h2 className="text-xl font-sans font-semibold text-textPrimary uppercase tracking-wide">
            Tracked Items <span className="text-neutral-600 text-sm ml-2">({items.length})</span>
          </h2>
          <button 
            onClick={fetchItems} 
            className="flex items-center gap-2 text-sm text-textSecondary hover:text-white transition-colors border-0 bg-transparent p-2"
          >
            <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
            Refresh
          </button>
        </div>

        {loading && items.length === 0 ? (
          <div className="py-20 flex justify-center text-neutral-500">
             <RefreshCw className="w-8 h-8 animate-spin" />
          </div>
        ) : items.length === 0 ? (
          <div className="py-20 text-center border border-dashed border-neutral-800 rounded-lg">
            <p className="text-textSecondary flex flex-col items-center gap-2">
               No products being tracked right now.
               <span className="text-sm">Add a URL above to start monitoring prices.</span>
            </p>
          </div>
        ) : (
          <div className="grid grid-cols-1 gap-4">
            {items.map((item) => (
              <ProductCard 
                key={item.id} 
                item={item} 
                onRemove={fetchItems}
              />
            ))}
          </div>
        )}
      </section>
      
    </div>
  );
}
