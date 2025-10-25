import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import Watches, { Watch } from './Watches';
import { http, HttpResponse } from 'msw';
import { setupServer } from 'msw/node';
import { API_URL } from '../config'; // Import API_URL from config
import { beforeAll, afterEach, afterAll, describe, it, expect } from 'vitest';

// Define the shape of a successful Watch response from the API
const mockWatch: Watch = {
  id: 1,
  origin: 'JFK',
  destination: 'LAX',
  departure_date: '2025-12-01',
  pax: 1,
  cabin: 'ECONOMY',
  auto_book_price: null,
  confirm_price: 300,
  currency: 'USD'
};

const server = setupServer(
  // Mock initial GET /watch
  http.get(`${API_URL}/watch`, () => {
    return HttpResponse.json([mockWatch]); // Return one watch
  }),
  // Mock POST /watch
  http.post(`${API_URL}/watch`, async () => {
    return HttpResponse.json(
      { ...mockWatch, id: 2 }, // Return a new watch
      { status: 200 } // Use 200 OK as defined by the backend
    );
  })
);

beforeAll(() => server.listen());
afterEach(() => server.resetHandlers());
afterAll(() => server.close());

describe('Watches Component (Flight Watch)', () => {
  it('renders the component with flight form fields', () => {
    render(<Watches />);
    expect(screen.getByText('My Flight Watches')).toBeInTheDocument();
    expect(screen.getByLabelText(/Origin/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/Destination/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/Departure Date/i)).toBeInTheDocument();
  });

  it('fetches and displays watches on load', async () => {
    render(<Watches />);
    
    // Check for the watch from our mock server
    expect(await screen.findByText('JFK to LAX')).toBeInTheDocument();
    expect(screen.getByText('Date: 2025-12-01')).toBeInTheDocument();
    expect(screen.getByText('Alert if under $300')).toBeInTheDocument();
  });

  it('displays an error message on failed fetch', async () => {
    server.use(
      http.get(`${API_URL}/watch`, () => {
        return new HttpResponse(null, { status: 500 });
      })
    );

    render(<Watches />);
    expect(await screen.findByText('Error: Failed to fetch watches')).toBeInTheDocument();
  });

it('shows form error if required fields are empty', async () => {
    render(<Watches />);
    
    await waitFor(() => {
      expect(screen.queryByText('Loading watches...')).not.toBeInTheDocument();
    });

    // --- START FIX ---
    // Find the form by its aria-label or role, and then fire the submit event.
    // The "Add New Flight Watch" heading is a good anchor.
const form = screen.getByTestId('add-watch-form');
    if (!form) {
      throw new Error('Could not find the form to test submission');
    }

    // This bypasses native HTML validation and tests your handleSubmit function directly.
    fireEvent.submit(form);
    // --- END FIX ---

    expect(await screen.findByText('Origin, Destination, and Date are required.')).toBeInTheDocument();
  });
  it('allows adding a new flight watch', async () => {
    render(<Watches />);
    // Wait for initial load
    await screen.findByText('JFK to LAX');
server.use(
    http.get(`${API_URL}/watch`, () => {
      return HttpResponse.json([
        mockWatch, // The original watch (price 300)
        // --- START FIX ---
        // Make the new watch match what the test submitted
        { 
          ...mockWatch, 
          id: 2, 
          origin: 'SFO', 
          destination: 'SEA', 
          confirm_price: 400 // <-- Set the correct price
        }
        // --- END FIX ---
      ]);
    })
  );

    // Fill out the form
  await userEvent.type(screen.getByLabelText(/Origin/i), 'SFO');
  await userEvent.type(screen.getByLabelText(/Destination/i), 'SEA');
  await userEvent.type(screen.getByLabelText(/Departure Date/i), '2026-02-01');
  await userEvent.type(screen.getByLabelText(/Confirm Price/i), '400');

  // Submit the form
  fireEvent.click(screen.getByRole('button', { name: /Add Watch/i }));

  // Wait for the new watch to appear in the list
  expect(await screen.findByText('SFO to SEA')).toBeInTheDocument();
  // This assertion will now pass
  expect(screen.getByText('Alert if under $400')).toBeInTheDocument();
  });
});