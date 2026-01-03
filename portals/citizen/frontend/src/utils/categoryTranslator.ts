/**
 * Utility functions to translate category and department names
 */

/**
 * Translate category name to Hindi
 */
export function translateCategory(category: string | undefined | null, currentLanguage: string): string {
  if (!category) return '';
  
  if (currentLanguage !== 'hi') {
    return category;
  }

  // Common category translations
  const categoryMap: Record<string, string> = {
    'Social Welfare': 'सामाजिक कल्याण',
    'Disability Support': 'विकलांगता सहायता',
    'Agriculture': 'कृषि',
    'Employment': 'रोजगार',
    'Education': 'शिक्षा',
    'Health': 'स्वास्थ्य',
    'Housing': 'आवास',
    'Financial Assistance': 'वित्तीय सहायता',
    'Women Empowerment': 'महिला सशक्तिकरण',
    'Senior Citizen': 'वरिष्ठ नागरिक',
    'Health and Medical': 'स्वास्थ्य और चिकित्सा',
    'Financial Aid': 'वित्तीय सहायता',
    'SOCIAL': 'सामाजिक कल्याण',
    'DISABILITY': 'विकलांगता सहायता',
    'AGRICULTURE': 'कृषि',
    'EMPLOYMENT': 'रोजगार',
    'EDUCATION': 'शिक्षा',
    'HEALTH': 'स्वास्थ्य',
    'HOUSING': 'आवास',
    'FINANCIAL': 'वित्तीय सहायता',
    'WOMEN': 'महिला सशक्तिकरण',
    'ELDERLY': 'वरिष्ठ नागरिक',
  };

  return categoryMap[category] || category;
}

/**
 * Translate department name to Hindi
 */
export function translateDepartment(department: string | undefined | null, currentLanguage: string): string {
  if (!department) return '';
  
  if (currentLanguage !== 'hi') {
    return department;
  }

  // Common department translations
  const departmentMap: Record<string, string> = {
    'Government of Rajasthan': 'राजस्थान सरकार',
    'Department of Social Welfare': 'सामाजिक कल्याण विभाग',
    'Department of Health': 'स्वास्थ्य विभाग',
    'Department of Education': 'शिक्षा विभाग',
    'Department of Agriculture': 'कृषि विभाग',
    'Department of Finance': 'वित्त विभाग',
  };

  return departmentMap[department] || department;
}

