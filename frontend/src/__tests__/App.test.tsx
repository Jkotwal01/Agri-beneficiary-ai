import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom';
import App from '../App';

describe('App', () => {
  it('renders without crash and shows Agri text', () => {
    render(<App />);
    expect(screen.getByText(/Hello Agri/i)).toBeInTheDocument();
  });
});
