import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import Watches, { Watch, TypicalBadge } from './Watches';
// --- START FIX ---
import { http, HttpResponse } from 'msw'; // Import 'http' and 'HttpResponse'
import { setupServer } from 'msw/node';    // Import setupServer from 'msw/node'
// --- END FIX ---

const API_URL = 'http://localhost:8000';

// --- START FIX: Update handlers to use 'http' and 'HttpResponse' ---
const server = setupServer(
  // Mock GET /watch
  http.get(`${API_URL}/watch`, () => {
    // Return an empty array initially
    return HttpResponse.json([]); 
  }),
  // Mock POST /watch
  http.post(`${API_URL}/watch`, async ({ request }) => {
    // You can optionally read the request body if needed: const newWatch = await request.json();
    // Return a successful response (e.g., status 201 Created)
    return new HttpResponse(null, { status: 201 }); 
  })
);

// --- END FIX ---

beforeAll(() => server.listen());
afterEach(() => server.resetHandlers());
afterAll(() => server.close());

describe('Watches Component', () => {
  // ... your existing test cases ...

  // Make sure tests using server.use also use the new syntax:
  it('fetches watches and displays them', async () => {
    server.use(
      // --- START FIX ---
      http.get(`${API_URL}/watch`, () => { // Use http.get
        const mockWatches: Watch[] = [
          { id: 1, origin: 'JFK', destination: 'LAX', departure_date: '2025-12-01' }, // Use correct fields
          { id: 2, origin: 'SFO', destination: 'SEA', departure_date: '2025-11-15' },
        ];
        return HttpResponse.json(mockWatches); // Use HttpResponse.json
      })
      // --- END FIX ---
    );

    render(<Watches />);
    // Update assertions to match flight data
    await waitFor(() => expect(screen.getByText('JFK to LAX on 2025-12-01')).toBeInTheDocument());
    expect(screen.getByText('SFO to SEA on 2025-11-15')).toBeInTheDocument();
  });

  // ... other tests ...

  it('allows adding a new watch', async () => {
    // Update this test to use flight fields
    render(<Watches />);
    await userEvent.type(screen.getByLabelText(/Origin/i), 'LHR');
    await userEvent.type(screen.getByLabelText(/Destination/i), 'CDG');
    await userEvent.type(screen.getByLabelText(/Departure Date/i), '2026-01-10');

    fireEvent.click(screen.getByText(/Add Watch/i));

    // You might need to adjust the server handler to return the new watch
    // or simply check that the loading state changes / form clears
    await waitFor(() => expect(screen.getByLabelText(/Origin/i)).toHaveValue('')); 
  });


});