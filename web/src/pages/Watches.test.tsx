import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import Watches from './Watches';
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

describe('Watches Page', () => {
  it('renders the page title', () => {
    render(<Watches />);
    expect(screen.getByText('My Watched Models')).toBeInTheDocument();
  });

  it('renders the Add New Watch form', () => {
    render(<Watches />);
    expect(screen.getByText('Add New Watch')).toBeInTheDocument();
    expect(screen.getByLabelText('Brand')).toBeInTheDocument();
    expect(screen.getByLabelText('Model')).toBeInTheDocument();
    expect(screen.getByLabelText('Reference Number')).toBeInTheDocument();
    expect(screen.getByText('Add Watch')).toBeInTheDocument();
  });

  it('allows the user to fill out the form and submit it', async () => {
    render(<Watches />);

    userEvent.type(screen.getByLabelText('Brand'), 'Rolex');
    userEvent.type(screen.getByLabelText('Model'), 'Submariner');
    userEvent.type(screen.getByLabelText('Reference Number'), '126610LN');

    fireEvent.click(screen.getByText('Add Watch'));

    await waitFor(() => {
      expect(screen.getByText('Add Watch')).toBeInTheDocument();
    });
  });

  it('displays an error message if the form is submitted with missing fields', async () => {
    render(<Watches />);

    fireEvent.click(screen.getByText('Add Watch'));

    await waitFor(() => {
      expect(screen.getByText('All fields are required.')).toBeInTheDocument();
    });
  });

  it('displays a message when there are no watches added yet', async () => {
    render(<Watches />);

    await waitFor(() => {
      expect(screen.getByText('No watches added yet')).toBeInTheDocument();
    });
  });

  it('fetches and displays watches from the API', async () => {
    server.use(
      rest.get(`${API_URL}/watch`, (req, res, ctx) => {
        return res(ctx.json([
          { id: 1, brand: 'Rolex', model: 'Submariner', reference_number: '126610LN' },
          { id: 2, brand: 'Omega', model: 'Seamaster', reference_number: '210.30.42.20.03.001' },
        ]));
      })
    );

    render(<Watches />);

    await waitFor(() => {
      expect(screen.getByText('Rolex Submariner')).toBeInTheDocument();
      expect(screen.getByText('Omega Seamaster')).toBeInTheDocument();
    });
  });

  it('displays a loading message while fetching watches', () => {
    render(<Watches />);
    expect(screen.getByText('Loading watches...')).toBeInTheDocument();
  });

  it('displays an error message if fetching watches fails', async () => {
    server.use(
      rest.get(`${API_URL}/watch`, (req, res, ctx) => {
        return res(ctx.status(500), ctx.json({ detail: 'Failed to fetch' }));
      })
    );

    render(<Watches />);

    await waitFor(() => {
      expect(screen.getByText('Error: Failed to fetch')).toBeInTheDocument();
    });
  });
});
