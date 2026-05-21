import { render, screen } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';

vi.mock('../pages/Dashboard', () => ({
  default: () => <div>Dashboard Mock</div>,
}));

import App from '../App';

describe('App', () => {
  it('renders the dashboard component', () => {
    render(<App />);
    expect(screen.getByText(/dashboard mock/i)).toBeInTheDocument();
  });
});
