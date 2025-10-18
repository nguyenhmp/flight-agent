

/* --- Agent change: Create Watch form & list --- */
// ERROR: OPENAI_API_KEY set, but 'openai' package is not installed. Run 'pip install openai'.


/* --- Agent change: Create Watch form & list --- */
// ERROR: OPENAI_API_KEY set, but 'openai' package is not installed. Run 'pip install openai'.


/* --- Agent change: Create Watch form & list --- */
// ERROR: OPENAI_API_KEY set, but 'openai' package is not installed. Run 'pip install openai'.


/* --- Agent change: Create Watch form & list --- */
import React, { useState, useEffect, FormEvent, ChangeEvent } from 'react';

interface TypicalPriceDetails {
  median: number;
  delta_percent: number;
}

interface Watch {
  id: number;
  brand: string;
  model: string;
  reference_number: string;
  typical_price_details?: TypicalPriceDetails;
}

const API_URL = 'http://localhost:8000';

const TypicalBadge: React.FC<{ details: TypicalPriceDetails }> = ({ details }) => {
  const delta = Math.round(details.delta_percent * 100);
  const isPositive = delta > 0;
  const colorClass = isPositive ? 'bg-red-100 text-red-800' : 'bg-green-100 text-green-800';
  const sign = isPositive ? '+' : '';

  return (
    <span className={`text-xs font-medium me-2 px-2.5 py-0.5 rounded ${colorClass}`}>
      {sign}{delta}% vs typical
    </span>
  );
};

const Watches: React.FC = () => {
  const [watches, setWatches] = useState<Watch[]>([]);
  const [newWatch, setNewWatch] = useState({ brand: '', model: '', reference_number: '' });
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [formError, setFormError] = useState<string | null>(null);

  const fetchWatches = async () => {
    try {
      setLoading(true);
      const response = await fetch(`${API_URL}/watch`);
      if (!response.ok) {
        throw new Error('Failed to fetch watches');
      }
      const data: Watch[] = await response.json();
      setWatches(data);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An unknown error occurred');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchWatches();
  }, []);

  const handleInputChange = (e: ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setNewWatch(prevState => ({ ...prevState, [name]: value }));
  };

  const handleSubmit = async (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setFormError(null);

    if (!newWatch.brand || !newWatch.model || !newWatch.reference_number) {
      setFormError('All fields are required.');
      return;
    }

    try {
      const response = await fetch(`${API_URL}/watch`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(newWatch),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to create watch');
      }

      setNewWatch({ brand: '', model: '', reference_number: '' });
      await fetchWatches();
    } catch (err) {
      setFormError(err instanceof Error ? err.message : 'An unknown error occurred');
    }
  };

  return (
    <div className="container mx-auto p-4 max-w-3xl">
      <h1 className="text-2xl font-bold mb-4">My Watched Models</h1>

      <div className="mb-8 p-4 border rounded-lg shadow-sm bg-white">
        <h2 className="text-xl font-semibold mb-2">Add New Watch</h2>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label htmlFor="brand" className="block text-sm font-medium text-gray-700">Brand</label>
            <input
              type="text"
              id="brand"
              name="brand"
              value={newWatch.brand}
              onChange={handleInputChange}
              className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
              placeholder="e.g., Rolex"
              required
              aria-label="Brand"
            />
          </div>
          <div>
            <label htmlFor="model" className="block text-sm font-medium text-gray-700">Model</label>
            <input
              type="text"
              id="model"
              name="model"
              value={newWatch.model}
              onChange={handleInputChange}
              className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
              placeholder="e.g., Submariner"
              required
              aria-label="Model"
            />
          </div>
          <div>
            <label htmlFor="reference_number" className="block text-sm font-medium text-gray-700">Reference Number</label>
            <input
              type="text"
              id="reference_number"
              name="reference_number"
              value={newWatch.reference_number}
              onChange={handleInputChange}
              className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
              placeholder="e.g., 126610LN"
              required
              aria-label="Reference Number"
            />
          </div>
          {formError && <p className="text-sm text-red-600">{formError}</p>}
          <button
            type="submit"
            className="inline-flex justify-center py-2 px-4 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
          >
            Add Watch
          </button>
        </form>
      </div>

      <div>
        <h2 className="text-xl font-semibold mb-2">Watch List</h2>
        {loading && <p>Loading watches...</p>}
        {error && <p className="text-red-600">Error: {error}</p>}
        {!loading && !error && watches.length === 0 && (
          <div className="text-center py-10 px-4 border-2 border-dashed rounded-lg">
            <h3 className="text-sm font-medium text-gray-900">No watches added yet</h3>
            <p className="mt-1 text-sm text-gray-500">Add a watch using the form above to start tracking.</p>
          </div>
        )}
        {!loading && !error && watches.length > 0 && (
          <ul className="space-y-3">
            {watches.map((watch) => (
              <li key={watch.id} className="bg-white shadow overflow-hidden rounded-md px-6 py-4 flex justify-between items-center">
                <div>
                  <p className="text-sm font-medium text-indigo-600 truncate">{watch.brand} {watch.model}</p>
                  <p className="mt-1 text-sm text-gray-500">{watch.reference_number}</p>
                </div>
                <div>
                  {watch.typical_price_details && <TypicalBadge details={watch.typical_price_details} />}
                </div>
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  );
};

export default Watches;
