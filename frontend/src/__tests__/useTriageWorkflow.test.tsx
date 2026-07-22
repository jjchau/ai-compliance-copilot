import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, it, vi, expect, beforeEach } from 'vitest';

vi.mock('../api/cases', () => ({
  getCases: vi.fn(),
  submitReview: vi.fn(),
}));

import { useTriageWorkflow } from '../hooks/useTriageWorkflow';
import * as casesApi from '../api/cases';

function HookTest() {
  const workflow = useTriageWorkflow();

  return (
    <div>
      <span data-testid="selected-trade">{workflow.selectedCase?.trade_id ?? 'none'}</span>
      <span data-testid="urgent-count">{workflow.urgentCases.length}</span>
      <span data-testid="queued-count">{workflow.queuedCases.length}</span>
      <span data-testid="reviewed-count">{workflow.reviewedCasesList.length}</span>
      <span data-testid="passed-count">{workflow.passedCasesList.length}</span>
      <span data-testid="notes">{workflow.caseStates['T1']?.notes ?? ''}</span>
      <span data-testid="reviewed-today">{workflow.reviewedTodayCount}</span>
      <button onClick={() => workflow.setView('active')}>Set Active</button>
      <button onClick={() => workflow.setView('reviewed')}>Set Reviewed</button>
      <button onClick={() => workflow.setView('passed')}>Set Passed</button>
      <button onClick={() => workflow.updateNotes('T1', 'updated')}>Update Notes</button>
      <button onClick={() => workflow.executeAction('T1', 'Reviewed', 'Approved', 'approved note')}>Approve T1</button>
      <button onClick={() => workflow.executeAction('T2', 'Reviewed', 'Rejected', 'rejected note')}>Reject T2</button>
      <button onClick={() => workflow.executeAction('T3', 'Escalated', 'Escalated', 'escalated note')}>Escalate T3</button>
      <button onClick={() => workflow.executeAction('T4', 'Reviewed', 'Approved', 'passed note')}>Approve T4</button>
    </div>
  );
}

describe('useTriageWorkflow', () => {
  const mockGetCases = vi.mocked(casesApi.getCases);
  const mockSubmitReview = vi.mocked(casesApi.submitReview);

  beforeEach(() => {
    mockGetCases.mockReset();
    mockSubmitReview.mockReset();
    mockSubmitReview.mockResolvedValue({});
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

    await userEvent.click(screen.getByText('Approve T1'));
    expect(mockSubmitReview).toHaveBeenCalledWith('T1', 'Approved', 'approved note', 'non-compliant');
    expect(screen.getByTestId('reviewed-today')).toHaveTextContent('1');
  });

  it('defaults active selection to urgent cases before queued cases', async () => {
    mockGetCases.mockResolvedValue([
      {
        trade_id: 'T1',
        escalation_level: 'urgent',
        priority_score: 2,
        compliance_label: 0,
        compliance_probability: 0.5,
        confidence_score: 0.9,
      },
      {
        trade_id: 'T2',
        escalation_level: 'queue',
        priority_score: 10,
        compliance_label: 1,
        compliance_probability: 0.9,
        confidence_score: 0.8,
      },
    ]);

    render(<HookTest />);

    await waitFor(() => expect(screen.getByTestId('selected-trade')).toHaveTextContent('T1'));
    expect(screen.getByTestId('urgent-count')).toHaveTextContent('1');
    expect(screen.getByTestId('queued-count')).toHaveTextContent('1');
  });

  it('defaults active selection to the first queued case when there are no urgent cases', async () => {
    mockGetCases.mockResolvedValue([
      {
        trade_id: 'T1',
        escalation_level: 'queue',
        priority_score: 3,
        compliance_label: 0,
        compliance_probability: 0.5,
        confidence_score: 0.9,
      },
      {
        trade_id: 'T2',
        escalation_level: 'priority',
        priority_score: 9,
        compliance_label: 1,
        compliance_probability: 0.9,
        confidence_score: 0.8,
      },
    ]);

    render(<HookTest />);

    await waitFor(() => expect(screen.getByTestId('selected-trade')).toHaveTextContent('T2'));
  });

  it('moves active selection to the next row in the same list after actions', async () => {
    mockGetCases.mockResolvedValue([
      {
        trade_id: 'T1',
        escalation_level: 'urgent',
        priority_score: 2,
        compliance_label: 0,
        compliance_probability: 0.5,
        confidence_score: 0.9,
      },
      {
        trade_id: 'T2',
        escalation_level: 'urgent',
        priority_score: 1,
        compliance_label: 1,
        compliance_probability: 0.9,
        confidence_score: 0.8,
      },
      {
        trade_id: 'T3',
        escalation_level: 'queue',
        priority_score: 5,
        compliance_label: 0,
        compliance_probability: 0.4,
        confidence_score: 0.7,
      },
    ]);

    render(<HookTest />);

    await waitFor(() => expect(screen.getByTestId('selected-trade')).toHaveTextContent('T1'));

    await userEvent.click(screen.getByText('Approve T1'));
    await waitFor(() => expect(screen.getByTestId('selected-trade')).toHaveTextContent('T2'));

    await userEvent.click(screen.getByText('Reject T2'));
    await waitFor(() => expect(screen.getByTestId('selected-trade')).toHaveTextContent('T3'));
  });

  it('defaults reviewed and passed tabs to their first visible row', async () => {
    mockGetCases.mockResolvedValue([
      {
        trade_id: 'T1',
        escalation_level: 'urgent',
        priority_score: 2,
        compliance_label: 0,
        compliance_probability: 0.5,
        confidence_score: 0.9,
      },
      {
        trade_id: 'T2',
        escalation_level: 'urgent',
        priority_score: 1,
        compliance_label: 1,
        compliance_probability: 0.9,
        confidence_score: 0.8,
      },
      {
        trade_id: 'T4',
        escalation_level: 'none',
        priority_score: 0,
        compliance_label: 1,
        compliance_probability: 0.95,
        confidence_score: 0.85,
      },
    ]);

    render(<HookTest />);

    await waitFor(() => expect(screen.getByTestId('selected-trade')).toHaveTextContent('T1'));

    await userEvent.click(screen.getByText('Set Passed'));
    expect(screen.getByTestId('selected-trade')).toHaveTextContent('T4');

    await userEvent.click(screen.getByText('Set Active'));
    await userEvent.click(screen.getByText('Approve T1'));
    await waitFor(() => expect(screen.getByTestId('reviewed-count')).toHaveTextContent('1'));

    await userEvent.click(screen.getByText('Set Reviewed'));
    expect(screen.getByTestId('selected-trade')).toHaveTextContent('T1');
  });

  it('moves reviewed and passed tab selections to the next row after actions', async () => {
    mockGetCases.mockResolvedValue([
      {
        trade_id: 'T1',
        escalation_level: 'urgent',
        priority_score: 2,
        compliance_label: 0,
        compliance_probability: 0.5,
        confidence_score: 0.9,
      },
      {
        trade_id: 'T2',
        escalation_level: 'urgent',
        priority_score: 1,
        compliance_label: 1,
        compliance_probability: 0.9,
        confidence_score: 0.8,
      },
      {
        trade_id: 'T4',
        escalation_level: 'none',
        priority_score: 0,
        compliance_label: 1,
        compliance_probability: 0.95,
        confidence_score: 0.85,
      },
    ]);

    render(<HookTest />);

    await waitFor(() => expect(screen.getByTestId('selected-trade')).toHaveTextContent('T1'));
    await userEvent.click(screen.getByText('Approve T1'));
    await waitFor(() => expect(screen.getByTestId('selected-trade')).toHaveTextContent('T2'));
    await userEvent.click(screen.getByText('Reject T2'));
    await waitFor(() => expect(screen.getByTestId('reviewed-count')).toHaveTextContent('2'));

    await userEvent.click(screen.getByText('Set Reviewed'));
    expect(screen.getByTestId('selected-trade')).toHaveTextContent('T1');

    await userEvent.click(screen.getByText('Approve T1'));
    await waitFor(() => expect(screen.getByTestId('selected-trade')).toHaveTextContent('T2'));

    await userEvent.click(screen.getByText('Set Passed'));
    expect(screen.getByTestId('selected-trade')).toHaveTextContent('T4');

    await userEvent.click(screen.getByText('Approve T4'));
    await waitFor(() => expect(screen.getByTestId('selected-trade')).toHaveTextContent('none'));
  });
});
