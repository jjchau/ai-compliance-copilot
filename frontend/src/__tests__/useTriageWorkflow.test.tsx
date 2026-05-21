import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, it, vi, expect, beforeEach } from 'vitest';

vi.mock('../api/cases', () => ({
  getCases: vi.fn(),
}));

import { useTriageWorkflow } from '../hooks/useTriageWorkflow';
import * as casesApi from '../api/cases';

function HookTest() {
  const workflow = useTriageWorkflow();

  return (
    <div>
      <span data-testid="selected-trade">{workflow.selectedCase?.trade_id ?? 'none'}</span>
      <span data-testid="urgent-count">{workflow.urgentCases.length}</span>
      <span data-testid="notes">{workflow.caseStates['T1']?.notes ?? ''}</span>
      <span data-testid="reviewed-today">{workflow.reviewedTodayCount}</span>
      <button onClick={() => workflow.setView('reviewed')}>Set Reviewed</button>
      <button onClick={() => workflow.updateNotes('T1', 'updated')}>Update Notes</button>
      <button onClick={() => workflow.executeAction('T1', 'Reviewed', 'Approved', 'approved note')}>Execute Action</button>
    </div>
  );
}

describe('useTriageWorkflow', () => {
  const mockGetCases = vi.mocked(casesApi.getCases);

  beforeEach(() => {
    mockGetCases.mockReset();
  });

  it('loads cases and exposes workflow state and actions', async () => {
    mockGetCases.mockResolvedValue([
      {
        trade_id: 'T1',
        escalation_level: 'urgent',
        priority_score: 2,
        compliance_probability: 0.5,
        confidence_score: 0.9,
      },
    ]);

    render(<HookTest />);

    await waitFor(() => expect(screen.getByTestId('selected-trade')).toHaveTextContent('T1'));
    expect(screen.getByTestId('urgent-count')).toHaveTextContent('1');

    await userEvent.click(screen.getByText('Set Reviewed'));
    expect(screen.getByTestId('selected-trade')).toHaveTextContent('none');

    await userEvent.click(screen.getByText('Update Notes'));
    expect(screen.getByTestId('notes')).toHaveTextContent('updated');

    await userEvent.click(screen.getByText('Execute Action'));
    expect(screen.getByTestId('reviewed-today')).toHaveTextContent('1');
  });
});
