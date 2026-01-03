// API Response Types (matching backend DTOs)

export interface ApiResponse<T> {
  success: boolean;
  message?: string;
  data?: T;
  timestamp?: string;
  errorCode?: string;
}

export interface PagedResponse<T> {
  content: T[];
  page: number;
  size: number;
  totalElements: number;
  totalPages: number;
  last: boolean;
  first: boolean;
}

// Auth Types
export interface TestTokenResponse {
  token: string;
  tokenType: string;
  username: string;
  expiresIn: string;
}

export interface LoginRequest {
  janAadhaarId?: string;
  otp?: string;
  username?: string;
  password?: string;
}

export interface LoginResponse {
  token: string;
  refreshToken: string;
  user: User;
}

// Citizen Types
export interface User {
  id: string;
  janAadhaarId?: string;
  fullName: string;
  fullNameHindi?: string;
  email?: string;
  mobileNumber: string;
  dateOfBirth?: string;
  gender?: 'MALE' | 'FEMALE' | 'OTHER';
  addressLine1?: string;
  addressLine2?: string;
  city?: string;
  district?: string;
  pincode?: string;
  status?: string;
  createdAt?: string;
  updatedAt?: string;
}

export interface CitizenRequest {
  mobileNumber: string;
  aadhaarNumber?: string;
  email?: string;
  fullName: string;
  dateOfBirth?: string;
  gender?: 'MALE' | 'FEMALE' | 'OTHER';
  addressLine1?: string;
  addressLine2?: string;
  city?: string;
  district?: string;
  pincode?: string;
}

export interface CitizenUpdateRequest {
  email?: string;
  fullName?: string;
  dateOfBirth?: string;
  gender?: 'MALE' | 'FEMALE' | 'OTHER';
  addressLine1?: string;
  addressLine2?: string;
  city?: string;
  district?: string;
  pincode?: string;
}

// Scheme Types
export interface Scheme {
  id: string;
  code: string;
  name: string;
  nameHindi?: string;
  description?: string;
  descriptionHindi?: string;
  category?: string;
  department?: string;
  eligibilityCriteria?: Record<string, any>;
  startDate?: string;
  endDate?: string;
  status: string;
  createdAt?: string;
  updatedAt?: string;
}

// Application Types
export interface ServiceApplication {
  id: string;
  applicationNumber?: string;
  citizenId: string;
  schemeId?: string;
  serviceType: string;
  applicationType?: string;
  subject?: string;
  description?: string;
  status: string;
  priority?: string;
  submittedAt?: string;
  expectedCompletionDate?: string;
  applicationData?: Record<string, any>;
  createdAt?: string;
  updatedAt?: string;
}

export interface ServiceApplicationRequest {
  schemeId?: string;
  serviceType: string;
  applicationType?: string;
  subject?: string;
  description?: string;
  priority?: string;
  expectedCompletionDate?: string;
  applicationData?: Record<string, any>;
}

export interface ApplicationStatusHistory {
  id: string;
  applicationId: string;
  fromStatus?: string;
  toStatus: string;
  stage?: string;
  comments?: string;
  changedBy?: string;
  changedByType?: string;
  changedAt: string;
  createdAt?: string;
  updatedAt?: string;
}

// Document Types
export interface Document {
  id: string;
  citizenId: string;
  applicationId?: string;
  documentType: string;
  documentName?: string;
  fileName?: string; // Alias for documentName for backward compatibility
  filePath?: string;
  fileSize?: number;
  mimeType?: string;
  fileHash?: string;
  verificationStatus: string;
  verifiedBy?: string;
  verifiedAt?: string;
  verificationNotes?: string;
  uploadedAt?: string;
  createdAt?: string;
  updatedAt?: string;
}

export interface DocumentRequest {
  applicationId?: string;
  documentType: string;
  fileName: string;
  file: File;
  metadata?: Record<string, any>;
}

// Notification Types
export interface Notification {
  id: string;
  citizenId: string;
  applicationId?: string;
  type: string;
  channel: string;
  subject?: string;
  message: string;
  status: string;
  isRead: boolean;
  sentAt?: string;
  deliveredAt?: string;
  readAt?: string;
  metadata?: Record<string, any>;
  createdAt?: string;
}

// Payment Types
export interface Payment {
  id: string;
  citizenId: string;
  applicationId?: string;
  transactionId: string;
  amount: number;
  currency: string;
  paymentMethod: string;
  status: string;
  description?: string;
  gatewayTransactionId?: string;
  gatewayResponse?: Record<string, any>;
  initiatedAt?: string;
  completedAt?: string;
  createdAt?: string;
}

export interface PaymentRequest {
  applicationId?: string;
  amount: number;
  currency?: string;
  paymentMethod: string;
  description?: string;
}

// Feedback Types
export interface Feedback {
  id: string;
  citizenId: string;
  applicationId?: string;
  type: string;
  category?: string;
  subject?: string;
  message: string;
  rating?: number;
  status: string;
  resolution?: string;
  resolvedBy?: string;
  resolvedAt?: string;
  createdAt?: string;
  updatedAt?: string;
}

export interface FeedbackRequest {
  type: string;
  category?: string;
  subject?: string;
  message: string;
  rating?: number;
  applicationId?: string | undefined;
}

// Profile Dashboard Types (AI-PLATFORM-02)
export interface FamilyMember {
  id: string;
  name: string;
  nameHindi?: string;
  relationship: string;
  age?: number;
  gender?: 'MALE' | 'FEMALE' | 'OTHER';
  confidence?: number;
  aadhaarNumber?: string;
  mobileNumber?: string;
  dateOfBirth?: string;
  incomeBand?: string;
  vulnerabilityCategory?: string;
}

export interface FamilyRelationship {
  from: string;
  to: string;
  relationship: string;
  confidence?: number;
}

export interface FamilyGraphResponse {
  members: FamilyMember[];
  relationships: FamilyRelationship[];
}

export interface BenefitAllocation {
  schemeId: string;
  schemeName: string;
  schemeNameHindi?: string;
  memberId: string;
  memberName: string;
  memberNameHindi?: string;
  amount: number;
  frequency: 'MONTHLY' | 'QUARTERLY' | 'YEARLY' | 'ONE_TIME';
}

export interface ConsentPreference {
  field: string;
  fieldLabel: string;
  enabled: boolean;
  source?: string;
}

export interface AuditEntry {
  id: string;
  field: string;
  fieldLabel: string;
  oldValue?: string;
  newValue?: string;
  oldConfidence?: number;
  newConfidence?: number;
  source: string;
  changedBy: string;
  changedByType: 'SYSTEM' | 'USER' | 'AUTOMATED';
  changedAt: string;
}

export interface MLSuggestedRelation {
  id: string;
  suggestedMember: {
    name: string;
    nameHindi?: string;
    aadhaarNumber?: string;
    mobileNumber?: string;
    age?: number;
    gender?: string;
  };
  suggestedRelationship: string;
  confidence: number;
  reasons: string[];
  matchScore: number;
}

