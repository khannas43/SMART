/**
 * Utility to format eligibility criteria from JSON to human-readable text
 */

export interface FormattedCriteria {
  label: string;
  value: string;
}

export function formatEligibilityCriteria(
  criteria: Record<string, any>,
  t?: (key: string, options?: any) => string
): FormattedCriteria[] {
  const formatted: FormattedCriteria[] = [];
  const translate = t || ((key: string) => key);

  // Age criteria
  if (criteria.min_age !== null && criteria.min_age !== undefined) {
    formatted.push({
      label: translate('schemes.eligibility.minAge', { defaultValue: 'Minimum Age' }),
      value: `${criteria.min_age} ${translate('schemes.eligibility.years', { defaultValue: 'years' })}`,
    });
  }
  if (criteria.max_age !== null && criteria.max_age !== undefined) {
    formatted.push({
      label: translate('schemes.eligibility.maxAge', { defaultValue: 'Maximum Age' }),
      value: `${criteria.max_age} ${translate('schemes.eligibility.years', { defaultValue: 'years' })}`,
    });
  }

  // Income criteria
  if (criteria.income_max !== null && criteria.income_max !== undefined) {
    formatted.push({
      label: translate('schemes.eligibility.maxIncome', { defaultValue: 'Maximum Annual Income' }),
      value: `₹${criteria.income_max.toLocaleString()}`,
    });
  }

  // Benefit information
  if (criteria.benefit_type) {
    formatted.push({
      label: translate('schemes.eligibility.benefitType', { defaultValue: 'Benefit Type' }),
      value: criteria.benefit_type,
    });
  }

  if (criteria.benefit_amount !== null && criteria.benefit_amount !== undefined) {
    formatted.push({
      label: translate('schemes.eligibility.benefitAmount', { defaultValue: 'Benefit Amount' }),
      value: `₹${criteria.benefit_amount.toLocaleString()}`,
    });
  }

  // BPL requirement
  if (criteria.bpl_required === true) {
    formatted.push({
      label: translate('schemes.eligibility.bplRequired', { defaultValue: 'BPL Card Required' }),
      value: translate('common.yes', { defaultValue: 'Yes' }),
    });
  } else if (criteria.bpl_required === false) {
    formatted.push({
      label: translate('schemes.eligibility.bplRequired', { defaultValue: 'BPL Card Required' }),
      value: translate('common.no', { defaultValue: 'No' }),
    });
  }

  // Target caste
  if (criteria.target_caste) {
    formatted.push({
      label: translate('schemes.eligibility.targetCaste', { defaultValue: 'Target Caste' }),
      value: criteria.target_caste,
    });
  }

  // Farmer requirement
  if (criteria.farmer_required === true) {
    formatted.push({
      label: translate('schemes.eligibility.farmerRequired', { defaultValue: 'Farmer Required' }),
      value: translate('common.yes', { defaultValue: 'Yes' }),
    });
  } else if (criteria.farmer_required === false) {
    formatted.push({
      label: translate('schemes.eligibility.farmerRequired', { defaultValue: 'Farmer Required' }),
      value: translate('common.no', { defaultValue: 'No' }),
    });
  }

  // House type requirement
  if (criteria.house_type_required) {
    formatted.push({
      label: translate('schemes.eligibility.houseTypeRequired', { defaultValue: 'House Type Required' }),
      value: criteria.house_type_required,
    });
  }

  // Minimum marks (for education schemes)
  if (criteria.min_marks !== null && criteria.min_marks !== undefined) {
    formatted.push({
      label: translate('schemes.eligibility.minMarks', { defaultValue: 'Minimum Marks' }),
      value: `${criteria.min_marks}%`,
    });
  }

  return formatted;
}

