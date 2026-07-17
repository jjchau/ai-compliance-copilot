import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import type { CaseAuditState, TradeCase } from '../hooks/useTriageWorkflow';

interface MockWorkflow {
  activeView: 'active' | 'reviewed' | 'passed';
  urgentCases: TradeCase[];
  queuedCases: TradeCase[];
  reviewedCasesList: TradeCase[];
  passedCasesList: TradeCase[];
  selectedCase: TradeCase | null;
  caseStates: Record<string, CaseAuditState>;
  reviewedTodayCount: number;
  setView: ReturnType<typeof vi.fn>;
  selectCase: ReturnType<typeof vi.fn>;
  updateNotes: ReturnType<typeof vi.fn>;
  executeAction: ReturnType<typeof vi.fn>;
}

const mockWorkflow: MockWorkflow = {
  activeView: 'active',
  urgentCases: [],
  queuedCases: [],
  reviewedCasesList: [],
  passedCasesList: [],
  selectedCase: null,
  caseStates: {},
  reviewedTodayCount: 0,
  setView: vi.fn(),
  selectCase: vi.fn(),
  updateNotes: vi.fn(),
  executeAction: vi.fn(),
};

vi.mock('../hooks/useTriageWorkflow', () => ({
  useTriageWorkflow: () => mockWorkflow,
}));

import Dashboard from '../pages/Dashboard';

describe('Dashboard', () => {
  beforeEach(() => {
    mockWorkflow.activeView = 'active';
    mockWorkflow.urgentCases = [];
    mockWorkflow.queuedCases = [];
    mockWorkflow.reviewedCasesList = [];
    mockWorkflow.passedCasesList = [];
    mockWorkflow.selectedCase = null;
    mockWorkflow.caseStates = {};
    mockWorkflow.setView.mockClear();
    mockWorkflow.updateNotes.mockClear();
    mockWorkflow.executeAction.mockClear();
  });

  it('renders the dashboard top counters and view buttons', () => {
    render(<Dashboard />);

    expect(screen.getByText(/AI Compliance Review Copilot/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /Active/i })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /Reviewed/i })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /Passed/i })).toBeInTheDocument();
  });

  it('calls setView when view buttons are clicked', async () => {
    render(<Dashboard />);

    await userEvent.click(screen.getByRole('button', { name: /Reviewed/i }));
    expect(mockWorkflow.setView).toHaveBeenCalledWith('reviewed');

    await userEvent.click(screen.getByRole('button', { name: /Passed/i }));
    expect(mockWorkflow.setView).toHaveBeenCalledWith('passed');
  });

  it('shows selected case details and updates notes', async () => {
    mockWorkflow.selectedCase = {
      trade_id: 'T1',
      trade_timestamp: '2026-05-21',
      compliance_probability: 0.9,
      confidence_score: 0.95,
      risk_score: 0.88,
      flag_reasons: 'Test reason',
      investment_type: 'Stocks',
      investment_amount: 1000,
      client_age: 40,
      client_income: 120000,
      risk_tolerance: 'Medium',
      investment_experience: 'Intermediate',
      investment_objective: 'Growth',
      investment_time_horizon: 'Medium',
      advisor_id: 'A1',
      advisor_experience: 'Mid',
      advisor_history_risk: 'Low',
      advisor_rationale: 'Rationale here',
      advisor_notes: 'Notes here',
      kyc_completeness: 'Complete',
      retrieved_policies: ['Policy A', 'Policy B'],
      compliance_label: true,
      priority_score: 1,
      escalation_level: 'queue'
    };
    mockWorkflow.caseStates = {
      T1: { reviewStatus: 'Not reviewed', notes: '' },
    };

    render(<Dashboard />);
    const input = screen.getByPlaceholderText(/Type definitive legal\/regulatory compliance assessment reasoning/i);

    await userEvent.type(input, 'Updated note');
    await userEvent.tab();

    expect(mockWorkflow.updateNotes).toHaveBeenCalledWith('T1', 'Updated note');
    expect(screen.getByText(/Policy A/i)).toBeInTheDocument();
    expect(screen.getByText(/Policy B/i)).toBeInTheDocument();
  });
});
