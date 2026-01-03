/**
 * Utility functions for handling localized content
 * Returns Hindi content when available and language is Hindi, otherwise returns English
 */

import { TFunction } from 'i18next';

/**
 * Get localized name (for schemes, citizens, etc.)
 * @param englishName - English name
 * @param hindiName - Hindi name (optional)
 * @param currentLanguage - Current i18n language code
 * @returns Localized name
 */
export function getLocalizedName(
  englishName: string | undefined | null,
  hindiName: string | undefined | null,
  currentLanguage: string
): string {
  if (!englishName) return '';
  
  // If language is Hindi and Hindi name exists, return Hindi name
  if (currentLanguage === 'hi' && hindiName) {
    return hindiName;
  }
  
  // Otherwise return English name
  return englishName;
}

/**
 * Get localized description
 * @param englishDescription - English description
 * @param hindiDescription - Hindi description (optional)
 * @param currentLanguage - Current i18n language code
 * @returns Localized description
 */
export function getLocalizedDescription(
  englishDescription: string | undefined | null,
  hindiDescription: string | undefined | null,
  currentLanguage: string
): string {
  if (!englishDescription) return '';
  
  // If language is Hindi and Hindi description exists, return Hindi description
  if (currentLanguage === 'hi' && hindiDescription) {
    return hindiDescription;
  }
  
  // Otherwise return English description
  return englishDescription;
}

/**
 * Get localized scheme name
 * @param scheme - Scheme object with name and nameHindi
 * @param currentLanguage - Current i18n language code
 * @returns Localized scheme name
 */
export function getSchemeName(scheme: { name: string; nameHindi?: string }, currentLanguage: string): string {
  return getLocalizedName(scheme.name, scheme.nameHindi, currentLanguage);
}

/**
 * Get localized scheme description
 * @param scheme - Scheme object with description and descriptionHindi
 * @param currentLanguage - Current i18n language code
 * @returns Localized scheme description
 */
export function getSchemeDescription(
  scheme: { description?: string; descriptionHindi?: string },
  currentLanguage: string
): string {
  return getLocalizedDescription(scheme.description, scheme.descriptionHindi, currentLanguage);
}

/**
 * Get localized user name
 * @param user - User object with fullName and fullNameHindi
 * @param currentLanguage - Current i18n language code
 * @returns Localized user name
 */
export function getUserName(
  user: { fullName: string; fullNameHindi?: string },
  currentLanguage: string
): string {
  return getLocalizedName(user.fullName, user.fullNameHindi, currentLanguage);
}

/**
 * Get localized feedback type label
 */
export function getFeedbackTypeLabel(type: string, t: TFunction): string {
  switch (type?.toUpperCase()) {
    case 'FEEDBACK':
      return t('feedback.type.feedback', { defaultValue: 'General Feedback' });
    case 'COMPLAINT':
      return t('feedback.type.complaint', { defaultValue: 'Complaint' });
    case 'SUGGESTION':
      return t('feedback.type.suggestion', { defaultValue: 'Suggestion' });
    case 'RATING':
      return t('feedback.type.rating', { defaultValue: 'Rating' });
    default:
      return type || '';
  }
}

/**
 * Get localized feedback category label
 */
export function getFeedbackCategoryLabel(category: string, t: TFunction): string {
  switch (category?.toUpperCase()) {
    case 'APPLICATION':
      return t('feedback.category.application', { defaultValue: 'Application' });
    case 'SCHEME':
      return t('feedback.category.scheme', { defaultValue: 'Scheme' });
    case 'DOCUMENT':
      return t('feedback.category.document', { defaultValue: 'Document' });
    case 'PAYMENT':
      return t('feedback.category.payment', { defaultValue: 'Payment' });
    case 'SERVICE':
      return t('feedback.category.service', { defaultValue: 'Service' });
    case 'OTHER':
      return t('feedback.category.other', { defaultValue: 'Other' });
    default:
      return category || '';
  }
}

/**
 * Get localized feedback status label
 */
export function getFeedbackStatusLabel(status: string, t: TFunction): string {
  switch (status?.toUpperCase()) {
    case 'PENDING':
      return t('feedback.status.pending', { defaultValue: 'Pending' });
    case 'IN_PROGRESS':
      return t('feedback.status.inProgress', { defaultValue: 'In Progress' });
    case 'RESOLVED':
      return t('feedback.status.resolved', { defaultValue: 'Resolved' });
    case 'CLOSED':
      return t('feedback.status.closed', { defaultValue: 'Closed' });
    default:
      return status || '';
  }
}

/**
 * Get localized help ticket status label
 */
export function getTicketStatusLabel(status: string, t: TFunction): string {
  switch (status?.toUpperCase()) {
    case 'OPEN':
      return t('help.status.open', { defaultValue: 'Open' });
    case 'IN_PROGRESS':
      return t('help.status.inProgress', { defaultValue: 'In Progress' });
    case 'RESOLVED':
      return t('help.status.resolved', { defaultValue: 'Resolved' });
    case 'CLOSED':
      return t('help.status.closed', { defaultValue: 'Closed' });
    default:
      return status || '';
  }
}

/**
 * Get localized help ticket priority label
 */
export function getTicketPriorityLabel(priority: string, t: TFunction): string {
  switch (priority?.toUpperCase()) {
    case 'LOW':
      return t('help.priority.low', { defaultValue: 'Low' });
    case 'MEDIUM':
      return t('help.priority.medium', { defaultValue: 'Medium' });
    case 'HIGH':
      return t('help.priority.high', { defaultValue: 'High' });
    case 'URGENT':
      return t('help.priority.urgent', { defaultValue: 'Urgent' });
    default:
      return priority || '';
  }
}

/**
 * Get localized help ticket category label
 */
export function getTicketCategoryLabel(category: string, t: TFunction): string {
  switch (category) {
    case 'Technical Issue':
      return t('help.category.technical', { defaultValue: 'Technical Issue' });
    case 'Application Inquiry':
      return t('help.category.application', { defaultValue: 'Application Inquiry' });
    case 'Document Issue':
      return t('help.category.document', { defaultValue: 'Document Issue' });
    case 'Payment Issue':
      return t('help.category.payment', { defaultValue: 'Payment Issue' });
    case 'Account Issue':
      return t('help.category.account', { defaultValue: 'Account Issue' });
    case 'Other':
      return t('help.category.other', { defaultValue: 'Other' });
    default:
      return category || '';
  }
}

/**
 * Get localized FAQ category label
 */
export function getFAQCategoryLabel(category: string, t: TFunction): string {
  switch (category) {
    case 'Applications':
      return t('help.category.applications', { defaultValue: 'Applications' });
    case 'Documents':
      return t('help.category.documents', { defaultValue: 'Documents' });
    case 'Benefits':
      return t('help.category.benefits', { defaultValue: 'Benefits' });
    case 'Profile':
      return t('help.category.profile', { defaultValue: 'Profile' });
    case 'Settings':
      return t('help.category.settings', { defaultValue: 'Settings' });
    case 'Authentication':
      return t('help.category.authentication', { defaultValue: 'Authentication' });
    default:
      return category || '';
  }
}

