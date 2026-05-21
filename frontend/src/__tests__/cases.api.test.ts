import { describe, it, expect, vi } from 'vitest';

vi.mock('axios', () => {
  const get = vi.fn(() => Promise.resolve({ data: [{ trade_id: 'T1' }] }));
  return {
    default: {
      create: vi.fn(() => ({ get })),
    },
  };
});

import axios from 'axios';
import { getCases } from '../api/cases';

describe('getCases API', () => {
  it('calls axios and returns response data', async () => {
    const data = await getCases();

    expect(data).toEqual([{ trade_id: 'T1' }]);
    expect(axios.create).toHaveBeenCalled();
  });
});
