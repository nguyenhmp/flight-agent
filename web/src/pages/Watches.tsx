/* --- Agent change: Create Flight form & list --- */
import React, { useState, useEffect, FormEvent, ChangeEvent } from 'react';
import { Optional } from '../types';

interface TypicalPriceDetails {
  median: number;
  delta_percent: number;
}

interface Flight {
  id: number;
  origin: string;
  destination: string;
  departure_date: string;
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

const Flights: React.FC = () => {
  const [flights, setFlights] = useState<Flight[]>([]);
  const [newFlight, setNewFlight] = useState({ origin: '', destination: '', departure_date: '' });
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<Optional<string>>(null);
  const [formError, setFormError] = useState<Optional<string>>(null);

  const fetchFlights = async () => {
    try {
      setLoading(true);
      const response = await fetch(`${API_URL}/watch`);
      if (!response.ok) {
        throw new Error('Failed to fetch flights');
      }
      const data: Flight[] = await response.json();
      setFlights(data);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An unknown error occurred');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchFlights();
  }, []);

  const handleInputChange = (e: ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setNewFlight(prevState => ({ ...prevState, [name]: value }));
  };

  const handleSubmit = async (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setFormError(null);

    if (!newFlight.origin || !newFlight.destination || !newFlight.departure_date) {
      setFormError('All fields are required.');
      return;
    }

    try {
      const response = await fetch(`${API_URL}/watch`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(newFlight),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to create flight');
      }

      setNewFlight({ origin: '', destination: '', departure_date: '' });
      await fetchFlights();
    } catch (err) {
      setFormError(err instanceof Error ? err.message : 'An unknown error occurred');
    }
  };

  return (
    <div className="container mx-auto p-4 max-w-3xl">
      <h1 className="text-2xl font-bold mb-4">My Watched Flights</h1>

      <div className="mb-8 p-4 border rounded-lg shadow-sm bg-white">
        <h2 className="text-xl font-semibold mb-2">Add New Flight</h2>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label htmlFor="origin" className="block text-sm font-medium text-gray-700">Origin</label>
            <input
              type="text"
              id="origin"
              name="origin"
              value={newFlight.origin}
              onChange={handleInputChange}
              className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
              placeholder="e.g., JFK"
              required
              aria-label="Origin"
            />
          </div>
          <div>
            <label htmlFor="destination" className="block text-sm font-medium text-gray-700">Destination</label>
            <input
              type="text"
              id="destination"
              name="destination"
              value={newFlight.destination}
              onChange={handleInputChange}
              className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
              placeholder="e.g., LAX"
              required
              aria-label="Destination"
            />
          </div>
          <div>
            <label htmlFor="departure_date" className="block text-sm font-medium text-gray-700">Departure Date</label>
            <input
              type="date"
              id="departure_date"
              name="departure_date"
              value={newFlight.departure_date}
              onChange={handleInputChange}
              className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
              required
              aria-label="Departure Date"
            />
          </div>
          {formError && <p className="text-sm text-red-600">{formError}</p>}
          <button
            type="submit"
            className="inline-flex justify-center py-2 px-4 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
          >
            Add Flight
          </button>
        </form>
      </div>

      <div>
        <h2 className="text-xl font-semibold mb-2">Flight List</h2>
        {loading && <p>Loading flights...</p>}
        {error && <p className="text-red-600">Error: {error}</p>}
        {!loading && !error && flights.length === 0 && (
          <div className="text-center py-10 px-4 border-2 border-dashed rounded-lg">
            <h3 className="text-sm font-medium text-gray-900">No flights added yet</h3>
            <p className="mt-1 text-sm text-gray-500">Add a flight using the form above to start tracking.</p>
          </div>
        )}
        {!loading && !error && flights.length > 0 && (
          <ul className="space-y-3">
            {flights.map((flight) => (
              <li key={flight.id} className="bg-white shadow overflow-hidden rounded-md px-6 py-4 flex justify-between items-center">
                <div>
                  <p className="text-sm font-medium text-indigo-600 truncate">{flight.origin} to {flight.destination}</p>
                  <p className="mt-1 text-sm text-gray-500">{flight.departure_date}</p>
                </div>
                <div>
                  {flight.typical_price_details && <TypicalBadge details={flight.typical_price_details} />}
                </div>
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  );
};

export default Flights;