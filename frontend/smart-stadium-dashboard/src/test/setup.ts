import '@testing-library/jest-dom';
import { vi } from 'vitest';

// Mock IntersectionObserver
if (!globalThis.IntersectionObserver) {
  globalThis.IntersectionObserver = vi.fn().mockImplementation(() => ({
    disconnect: vi.fn(),
    observe: vi.fn(),
    unobserve: vi.fn(),
    root: null,
    rootMargin: '0px',
    thresholds: [],
    takeRecords: vi.fn().mockReturnValue([]),
  }));
}

// Mock ResizeObserver
if (!globalThis.ResizeObserver) {
  globalThis.ResizeObserver = vi.fn().mockImplementation(() => ({
    disconnect: vi.fn(),
    observe: vi.fn(),
    unobserve: vi.fn(),
  }));
}

// Mock matchMedia
Object.defineProperty(window, 'matchMedia', {
  writable: true,
  value: vi.fn().mockImplementation((query: string) => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: vi.fn(),
    removeListener: vi.fn(),
    addEventListener: vi.fn(),
    removeEventListener: vi.fn(),
    dispatchEvent: vi.fn(),
  })),
});

// Mock scrollTo
Object.defineProperty(window, 'scrollTo', {
  writable: true,
  value: vi.fn(),
});