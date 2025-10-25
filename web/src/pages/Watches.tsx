import React, { useState, useEffect, FormEvent, ChangeEvent } from 'react';
import { API_URL } from '../config'; // Import the API URL

// Interface for what the API will return
export interface Watch {
  id: number;
  origin: string;
  destination: string;
  departure_date: string;
  pax: number;
  cabin: string;
  auto_book_price?: number | null;
  confirm_price?: number | null;
  currency: string;
}

// Interface for the form state
interface WatchFormState {
  origin: string;
  destination: string;
  departure_date: string;
  pax: number;
  cabin: string;
  confirm_price: string; // Use string for form input
}

const Watches: React.FC = () => {
  const [watches, setWatches] = useState<Watch[]>([]);
  
  // Set initial state matching the API schema
  const initialState: WatchFormState = {
    origin: '',
    destination: '',
    departure_date: '',
    pax: 1,
    cabin: 'ECONOMY',
    confirm_price: ''
  };
  
  const [newWatch, setNewWatch] = useState(initialState);
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

  const handleInputChange = (e: ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setNewWatch(prevState => ({ 
      ...prevState, 
      [name]: name === 'pax' ? parseInt(value, 10) : value 
    }));
  };

  const handleSubmit = async (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setFormError(null);

    // This check now matches the test's expectation
    if (!newWatch.origin || !newWatch.destination || !newWatch.departure_date) {
      setFormError('Origin, Destination, and Date are required.');
      return;
    }

    try {
      // Prepare payload for the API
      const payload = {
        ...newWatch,
        confirm_price: newWatch.confirm_price ? parseFloat(newWatch.confirm_price) : null,
        auto_book_price: null 
      };

      const response = await fetch(`${API_URL}/watch`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(payload),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to create watch');
      }

      setNewWatch(initialState); // Reset form
      await fetchWatches();
    } catch (err) {
      setFormError(err instanceof Error ? err.message : 'An unknown error occurred');
    }
  };

  return (
    <div className="container mx-auto p-4 max-w-3xl">
      <h1 className="text-2xl font-bold mb-4">My Flight Watches</h1>

      <div className="mb-8 p-4 border rounded-lg shadow-sm bg-white">
        <h2 className="text-xl font-semibold mb-2">Add New Flight Watch</h2>
<form onSubmit={handleSubmit} className="space-y-4" data-testid="add-watch-form">          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label htmlFor="origin" className="block text-sm font-medium text-gray-700">Origin (IATA)</label>
              <input
                type="text" id="origin" name="origin"
                value={newWatch.origin} onChange={handleInputChange}
                className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
                placeholder="e.g., JFK" required maxLength={3}
                aria-label="Origin (IATA)"
              />
            </div>
            <div>
              <label htmlFor="destination" className="block text-sm font-medium text-gray-700">Destination (IATA)</label>
              <input
                type="text" id="destination" name="destination"
                value={newWatch.destination} onChange={handleInputChange}
                className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
                placeholder="e.g., LAX" required maxLength={3}
                aria-label="Destination (IATA)"
              />
            </div>
          </div>

          <div>
            <label htmlFor="departure_date" className="block text-sm font-medium text-gray-700">Departure Date</label>
            <input
              type="date" id="departure_date" name="departure_date"
              value={newWatch.departure_date} onChange={handleInputChange}
              className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
              required aria-label="Departure Date"
            />
          </div>

          <div>
            <label htmlFor="confirm_price" className="block text-sm font-medium text-gray-700">Confirm Price (USD)</label>
            <input
              type="number" id="confirm_price" name="confirm_price"
              value={newWatch.confirm_price} onChange={handleInputChange}
              className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
              placeholder="e.g., 250" aria-label="Confirm Price"
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
              <li key={watch.id} className="bg-white shadow overflow-hidden rounded-md px-6 py-4">
                <div>
                  <p className="text-sm font-medium text-indigo-600 truncate">{watch.origin} to {watch.destination}</p>
                  <p className="mt-1 text-sm text-gray-500">Date: {watch.departure_date}</p>
                  {watch.confirm_price && (
                     <p className="mt-1 text-sm text-gray-500">Alert if under ${watch.confirm_price}</p>
                  )}
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