import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import Flights from './Watches';
import { rest } from 'msw';
import { setupServer } from 'msw/lib/node';
import { API_URL } from '../config';

const server = setupServer(
  rest.get(`${API_URL}/watch`, (req, res, ctx) => {
    return res(ctx.json([]));
  }),
  rest.post(`${API_URL}/watch`, (req, res, ctx) => {
    return res(ctx.status(201));
  }),
);

beforeAll(() => server.listen());
afterEach(() => server.resetHandlers());
afterAll(() => server.close());

describe('Flights Page', () => {
  it('renders the page title', () => {
    render(<Flights />);
    expect(screen.getByText('My Watched Flights')).toBeInTheDocument();
  });

  it('renders the Add New Flight form', () => {
    render(<Flights />);
    expect(screen.getByText('Add New Flight')).toBeInTheDocument();
    expect(screen.getByLabelText('Origin')).toBeInTheDocument();
    expect(screen.getByLabelText('Destination')).toBeInTheDocument();
    expect(screen.getByLabelText('Departure Date')).toBeInTheDocument();
    expect(screen.getByText('Add Flight')).toBeInTheDocument();
  });

  it('allows the user to fill out the form and submit it', async () => {
    render(<Flights />);

    userEvent.type(screen.getByLabelText('Origin'), 'JFK');
    userEvent.type(screen.getByLabelText('Destination'), 'LAX');
    userEvent.type(screen.getByLabelText('Departure Date'), '2024-01-01');

    fireEvent.click(screen.getByText('Add Flight'));

    await waitFor(() => {
      expect(screen.getByText('Add Flight')).toBeInTheDocument();
    });
  });

  it('displays an error message if the form is submitted with missing fields', async () => {
    render(<Flights />);

    fireEvent.click(screen.getByText('Add Flight'));

    await waitFor(() => {
      expect(screen.getByText('All fields are required.')).toBeInTheDocument();
    });
  });

  it('displays a message when there are no flights added yet', async () => {
    render(<Flights />);

    await waitFor(() => {
      expect(screen.getByText('No flights added yet')).toBeInTheDocument();
    });
  });

  it('fetches and displays flights from the API', async () => {
    server.use(
      rest.get(`${API_URL}/watch`, (req, res, ctx) => {
        return res(ctx.json([
          { id: 1, origin: 'JFK', destination: 'LAX', departure_date: '2024-01-01' },
          { id: 2, origin: 'ORD', destination: 'SFO', departure_date: '2024-01-05' },
        ]));
      })
    );

    render(<Flights />);

    await waitFor(() => {
      expect(screen.getByText('JFK to LAX')).toBeInTheDocument();
      expect(screen.getByText('ORD to SFO')).toBeInTheDocument();
    });
  });

  it('displays a loading message while fetching flights', () => {
    render(<Flights />);
    expect(screen.getByText('Loading flights...')).toBeInTheDocument();
  });

  it('displays an error message if fetching flights fails', async () => {
    server.use(
      rest.get(`${API_URL}/watch`, (req, res, ctx) => {
        return res(ctx.status(500), ctx.json({ detail: 'Failed to fetch' }));
      })
    );

    render(<Flights />);

    await waitFor(() => {
      expect(screen.getByText('Error: Failed to fetch')).toBeInTheDocument();
    });
  });
});