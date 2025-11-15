import { describe, it, expect } from 'vitest';
import { landingPageLabels } from '../utils/landingPageLabels';

describe('landingPageLabels', () => {
  it('returns translated labels', () => {
    const t = (key: string) => key;
    const result = landingPageLabels(t);
    expect(result).toHaveLength(2);
    expect(result[0]).toEqual({ value: 'dashboard', label: 'profile.landing.dashboard' });
    expect(result[1]).toEqual({ value: 'search', label: 'profile.landing.search' });
  });
});
