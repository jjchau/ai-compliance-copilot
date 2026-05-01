import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from src.policy.policy_corpus import POLICY_CORPUS


class TestPolicyCorpusStructure:
    """Test the structure and integrity of POLICY_CORPUS."""

    def test_policy_corpus_exists(self):
        """Test that POLICY_CORPUS is defined and is a dictionary."""
        assert POLICY_CORPUS is not None
        assert isinstance(POLICY_CORPUS, dict)

    def test_policy_corpus_not_empty(self):
        """Test that POLICY_CORPUS contains policies."""
        assert len(POLICY_CORPUS) > 0

    def test_policy_keys_are_strings(self):
        """Test that all policy keys are strings."""
        for key in POLICY_CORPUS.keys():
            assert isinstance(key, str)

    def test_policy_ids_have_correct_format(self):
        """Test that all policy IDs follow naming convention."""
        valid_prefixes = [
            'POLICY_KYC_',
            'POLICY_SUIT_',
            'POLICY_EXP_',
            'POLICY_RISK_',
            'POLICY_DOC_',
            'POLICY_SUP_',
            'POLICY_CLIENT_'
        ]
        for policy_id in POLICY_CORPUS.keys():
            assert any(policy_id.startswith(prefix) for prefix in valid_prefixes), \
                f"Policy ID {policy_id} does not match expected format"

    def test_all_policies_have_required_fields(self):
        """Test that each policy has all required fields."""
        required_fields = {'title', 'category', 'text', 'severity', 'tags'}
        
        for policy_id, policy in POLICY_CORPUS.items():
            assert isinstance(policy, dict), f"Policy {policy_id} is not a dict"
            for field in required_fields:
                assert field in policy, f"Policy {policy_id} missing field: {field}"

    def test_policy_title_is_string(self):
        """Test that all policy titles are non-empty strings."""
        for policy_id, policy in POLICY_CORPUS.items():
            assert isinstance(policy['title'], str), \
                f"Policy {policy_id} title is not a string"
            assert len(policy['title']) > 0, \
                f"Policy {policy_id} title is empty"

    def test_policy_category_is_string(self):
        """Test that all policy categories are non-empty strings."""
        for policy_id, policy in POLICY_CORPUS.items():
            assert isinstance(policy['category'], str), \
                f"Policy {policy_id} category is not a string"
            assert len(policy['category']) > 0, \
                f"Policy {policy_id} category is empty"

    def test_policy_text_is_string(self):
        """Test that all policy texts are non-empty strings."""
        for policy_id, policy in POLICY_CORPUS.items():
            assert isinstance(policy['text'], str), \
                f"Policy {policy_id} text is not a string"
            assert len(policy['text']) > 0, \
                f"Policy {policy_id} text is empty"

    def test_policy_severity_is_valid(self):
        """Test that all policy severities are valid values."""
        valid_severities = {'critical', 'high', 'medium', 'low'}
        
        for policy_id, policy in POLICY_CORPUS.items():
            assert policy['severity'] in valid_severities, \
                f"Policy {policy_id} has invalid severity: {policy['severity']}"

    def test_policy_tags_is_list(self):
        """Test that all policy tags are lists."""
        for policy_id, policy in POLICY_CORPUS.items():
            assert isinstance(policy['tags'], list), \
                f"Policy {policy_id} tags is not a list"

    def test_policy_tags_not_empty(self):
        """Test that all policy tags lists are non-empty."""
        for policy_id, policy in POLICY_CORPUS.items():
            assert len(policy['tags']) > 0, \
                f"Policy {policy_id} has no tags"

    def test_policy_tags_are_strings(self):
        """Test that all tags are strings."""
        for policy_id, policy in POLICY_CORPUS.items():
            for tag in policy['tags']:
                assert isinstance(tag, str), \
                    f"Policy {policy_id} has non-string tag: {tag}"

    def test_policy_ids_are_unique(self):
        """Test that all policy IDs are unique."""
        policy_ids = list(POLICY_CORPUS.keys())
        assert len(policy_ids) == len(set(policy_ids)), \
            "Duplicate policy IDs found"

    def test_policy_id_matches_title_convention(self):
        """Test that policy IDs and titles follow consistent conventions."""
        # Each policy ID should be related to its category
        for policy_id, policy in POLICY_CORPUS.items():
            category = policy['category']
            # ID should start with a category indicator
            if category == 'KYC':
                assert 'KYC' in policy_id, f"Policy {policy_id} KYC policy should have KYC in ID"
            elif category == 'Suitability':
                assert any(x in policy_id for x in ['SUIT', 'EXP', 'CLIENT']), \
                    f"Policy {policy_id} Suitability policy should have SUIT/EXP/CLIENT in ID"


class TestPoliciesByCategory:
    """Test organization of policies by category."""

    def test_kyc_policies_exist(self):
        """Test that KYC policies are defined."""
        kyc_policies = [p for p in POLICY_CORPUS.values() if p['category'] == 'KYC']
        assert len(kyc_policies) > 0, "No KYC policies found"

    def test_suitability_policies_exist(self):
        """Test that Suitability policies are defined."""
        suitability_policies = [p for p in POLICY_CORPUS.values() if p['category'] == 'Suitability']
        assert len(suitability_policies) > 0, "No Suitability policies found"

    def test_risk_policies_exist(self):
        """Test that Risk policies are defined."""
        risk_policies = [p for p in POLICY_CORPUS.values() if p['category'] == 'Risk']
        assert len(risk_policies) > 0, "No Risk policies found"

    def test_documentation_policies_exist(self):
        """Test that Documentation policies are defined."""
        doc_policies = [p for p in POLICY_CORPUS.values() if p['category'] == 'Documentation']
        assert len(doc_policies) > 0, "No Documentation policies found"

    def test_supervision_policies_exist(self):
        """Test that Supervision policies are defined."""
        sup_policies = [p for p in POLICY_CORPUS.values() if p['category'] == 'Supervision']
        assert len(sup_policies) > 0, "No Supervision policies found"

    def test_all_categories_have_consistent_names(self):
        """Test that category names are consistent across policies."""
        categories = set(p['category'] for p in POLICY_CORPUS.values())
        assert categories.issubset({
            'KYC',
            'Suitability',
            'Risk',
            'Documentation',
            'Supervision'
        }), f"Unexpected categories found: {categories}"


class TestSpecificPolicies:
    """Test specific policies exist with correct content."""

    def test_kyc_001_exists(self):
        """Test that critical KYC completeness policy exists."""
        assert 'POLICY_KYC_001' in POLICY_CORPUS
        policy = POLICY_CORPUS['POLICY_KYC_001']
        assert policy['severity'] == 'critical'
        assert 'kyc' in policy['tags']

    def test_suitability_001_exists(self):
        """Test that critical suitability policy exists."""
        assert 'POLICY_SUIT_001' in POLICY_CORPUS
        policy = POLICY_CORPUS['POLICY_SUIT_001']
        assert policy['severity'] == 'critical'
        assert 'suitability' in policy['tags']

    def test_experience_001_exists(self):
        """Test that critical experience policy exists."""
        assert 'POLICY_EXP_001' in POLICY_CORPUS
        policy = POLICY_CORPUS['POLICY_EXP_001']
        assert policy['severity'] == 'critical'
        assert 'experience' in policy['tags']

    def test_client_interest_001_exists(self):
        """Test that fiduciary duty policy exists."""
        assert 'POLICY_CLIENT_001' in POLICY_CORPUS
        policy = POLICY_CORPUS['POLICY_CLIENT_001']
        assert policy['severity'] == 'critical'
        assert 'fiduciary' in policy['tags']

    def test_critical_policies_count(self):
        """Test that there are sufficient critical policies."""
        critical_policies = [p for p in POLICY_CORPUS.values() if p['severity'] == 'critical']
        assert len(critical_policies) >= 4, "Expected at least 4 critical policies"


class TestPolicySeverityDistribution:
    """Test distribution of policy severities."""

    def test_at_least_one_critical_policy(self):
        """Test that at least one critical policy exists."""
        critical = [p for p in POLICY_CORPUS.values() if p['severity'] == 'critical']
        assert len(critical) > 0

    def test_at_least_one_high_policy(self):
        """Test that at least one high severity policy exists."""
        high = [p for p in POLICY_CORPUS.values() if p['severity'] == 'high']
        assert len(high) > 0

    def test_at_least_one_medium_policy(self):
        """Test that at least one medium severity policy exists."""
        medium = [p for p in POLICY_CORPUS.values() if p['severity'] == 'medium']
        assert len(medium) > 0

    def test_severity_distribution(self):
        """Test that severities are appropriately distributed."""
        severities = [p['severity'] for p in POLICY_CORPUS.values()]
        assert len(severities) >= 5, "Expected at least 5 policies"
        
        # Most policies should be high or higher
        high_or_critical = sum(1 for s in severities if s in ['critical', 'high'])
        assert high_or_critical >= len(severities) * 0.6, \
            "At least 60% of policies should be critical or high"


class TestPolicyTags:
    """Test consistency and coverage of policy tags."""

    def test_all_common_tags_are_present(self):
        """Test that common compliance-related tags are used."""
        all_tags = set()
        for policy in POLICY_CORPUS.values():
            all_tags.update(policy['tags'])
        
        expected_tags = {'kyc', 'suitability', 'documentation', 'risk'}
        assert expected_tags.issubset(all_tags), \
            f"Missing expected tags: {expected_tags - all_tags}"

    def test_no_duplicate_tags_in_single_policy(self):
        """Test that no policy has duplicate tags."""
        for policy_id, policy in POLICY_CORPUS.items():
            tags = policy['tags']
            assert len(tags) == len(set(tags)), \
                f"Policy {policy_id} has duplicate tags"

    def test_tags_are_lowercase(self):
        """Test that all tags are lowercase for consistency."""
        for policy_id, policy in POLICY_CORPUS.items():
            for tag in policy['tags']:
                assert tag == tag.lower(), \
                    f"Policy {policy_id} has non-lowercase tag: {tag}"


class TestPolicyAccessibility:
    """Test that policies can be accessed and used programmatically."""

    def test_can_iterate_all_policies(self):
        """Test that all policies can be iterated."""
        count = 0
        for policy_id, policy in POLICY_CORPUS.items():
            assert policy_id.startswith('POLICY_')
            assert 'title' in policy
            count += 1
        assert count > 0

    def test_can_access_policy_by_id(self):
        """Test that policies can be accessed by their ID."""
        kyc_policies = {k: v for k, v in POLICY_CORPUS.items() if 'KYC' in k}
        assert len(kyc_policies) > 0
        
        for policy_id in kyc_policies.keys():
            assert POLICY_CORPUS[policy_id]['category'] == 'KYC'

    def test_policy_corpus_is_immutable_by_design(self):
        """Test that accessing POLICY_CORPUS doesn't break on repeated access."""
        first_access = len(POLICY_CORPUS)
        second_access = len(POLICY_CORPUS)
        assert first_access == second_access, "POLICY_CORPUS size changed"
