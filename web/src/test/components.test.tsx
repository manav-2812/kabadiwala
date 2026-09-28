import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import React from 'react';
import { WeightStepper } from '../design/components/WeightStepper';
import { VoiceButton } from '../design/components/VoiceButton';

describe('WeightStepper Component (§3.2)', () => {
  it('renders current weight in kilograms', () => {
    render(<WeightStepper valueGrams={5000} onChange={vi.fn()} />);
    expect(screen.getByText('5')).toBeInTheDocument();
    expect(screen.getByText('kg')).toBeInTheDocument();
  });

  it('increments by 0.5 kg (500g) on plus click', () => {
    const handleChange = vi.fn();
    render(<WeightStepper valueGrams={2000} onChange={handleChange} />);
    const buttons = screen.getAllByRole('button');
    // Button 0 = Minus, Button 1 = VoiceButton (Listen), Button 2 = Plus
    const plusBtn = buttons[2];
    fireEvent.click(plusBtn);
    expect(handleChange).toHaveBeenCalledWith(2500);
  });

  it('decrements by 0.5 kg (500g) on minus click', () => {
    const handleChange = vi.fn();
    render(<WeightStepper valueGrams={2000} onChange={handleChange} />);
    const buttons = screen.getAllByRole('button');
    // Button 0 = Minus
    const minusBtn = buttons[0];
    fireEvent.click(minusBtn);
    expect(handleChange).toHaveBeenCalledWith(1500);
  });

  it('disables minus button at minGrams boundary', () => {
    render(<WeightStepper valueGrams={500} minGrams={500} onChange={vi.fn()} />);
    const buttons = screen.getAllByRole('button');
    expect(buttons[0]).toBeDisabled();
  });

  it('allows clicking quick presets (e.g. 10 kg)', () => {
    const handleChange = vi.fn();
    render(<WeightStepper valueGrams={2000} onChange={handleChange} />);
    const preset10 = screen.getByText(/10\s*kg/);
    fireEvent.click(preset10);
    expect(handleChange).toHaveBeenCalledWith(10000);
  });
});

describe('VoiceButton Component (§3.2)', () => {
  it('renders button with accessible label', () => {
    render(<VoiceButton text="5 kilograms circuit board" />);
    const btn = screen.getByRole('button', { name: /read aloud/i });
    expect(btn).toBeInTheDocument();
  });

  it('calls speak on click without bubbling', () => {
    const speakSpy = vi.spyOn(window.speechSynthesis, 'speak');
    render(<VoiceButton text="Test voice announcement" />);
    const btn = screen.getByRole('button', { name: /read aloud/i });
    fireEvent.click(btn);
    expect(speakSpy).toHaveBeenCalled();
  });
});
