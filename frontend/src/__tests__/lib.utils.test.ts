import { describe, it, expect } from 'vitest';
import { cn } from '../lib/utils';

describe('cn helper', () => {
  it('joins class names into a single string', () => {
    expect(cn('foo', 'bar', 'foo')).toBe('foo bar foo');
  });

  it('returns an empty string when no classes are passed', () => {
    expect(cn()).toBe('');
  });
});
