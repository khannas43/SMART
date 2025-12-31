# Citizen Portal Screen to AI/ML Use Case Mapping Template

**Purpose:** Document mapping of 20 Citizen Portal screens to AI/ML use cases  
**Created:** 2024-12-30  
**For:** Citizen Portal Development Team  
**Version:** 1.0

---

## Instructions for Portal Agent

Please fill out this template for each of the 20 Citizen Portal screens:

1. **Screen Name & ID** - Official screen identifier
2. **Screen Purpose** - What the screen does
3. **AI/ML Use Cases** - Which use cases this screen will use
4. **API Integration** - Specific API calls needed
5. **Data Flow** - Sequence of operations
6. **UI Components** - What data/components will be displayed
7. **User Actions** - What users can do and what it triggers

After completing this mapping, the AI/ML team will:
- Review the mapping
- Suggest innovative/advanced features
- Identify optimization opportunities
- Recommend additional AI/ML capabilities

---

## Screen Mapping Template

### Screen 1: [Screen Name]

**Screen ID:** [e.g., CIT-PROF-01]  
**Screen Name:** [Full screen name]  
**Purpose:** [Brief description of what this screen does]

**AI/ML Use Cases Used:**
- **AI-PLATFORM-XX:** [How this use case is used on this screen]
  - Primary function: [e.g., Display eligibility hints]
  - Data shown: [e.g., Top 5 eligible schemes]
- **AI-PLATFORM-YY:** [Another use case if applicable]
  - Primary function: [e.g., Show profile data]
  - Data shown: [e.g., Income band, vulnerability status]

**API Integration:**
1. `GET /api/v1/...` - [Purpose, when called]
   - Request params: [list]
   - Response used for: [what UI component]
2. `POST /api/v1/...` - [Purpose, when called]
   - Request body: [structure]
   - Response used for: [what UI component]

**Data Flow:**
1. User opens screen → Load [data from use case X]
2. User clicks [action] → Call [API Y]
3. [API response] → Update [UI component Z]

**UI Components:**
- **[Component Name 1]** (e.g., Eligibility Cards)
  - Shows: [Data from AI-PLATFORM-03]
  - Updates: [When/how it updates]
- **[Component Name 2]** (e.g., Profile Summary)
  - Shows: [Data from AI-PLATFORM-02]
  - Updates: [When/how it updates]

**User Actions:**
- **[Action 1]** (e.g., Click "Check Eligibility")
  - Triggers: `POST /api/v1/eligibility/check`
  - Updates: [Which components]
- **[Action 2]** (e.g., View Details)
  - Triggers: `GET /api/v1/...`
  - Updates: [Which components]

**Dependencies:**
- Requires: [Any prerequisites]
- Depends on: [Other screens/use cases]

**Notes:**
- [Any special considerations]
- [Future enhancements planned]

---

### Screen 2: [Screen Name]

[Repeat template above]

---

### Screen 3: [Screen Name]

[Repeat template above]

---

## Summary Matrix

After completing all 20 screens, create a summary:

| Screen ID | Screen Name | Primary Use Cases | Secondary Use Cases | Integration Complexity |
|-----------|-------------|-------------------|---------------------|----------------------|
| CIT-PROF-01 | Profile Dashboard | AI-02, AI-03 | AI-08 | Medium |
| ... | ... | ... | ... | ... |

---

## Integration Priority

After mapping, categorize screens by integration priority:

### High Priority (Core Functionality)
- [List screens that are critical for portal launch]

### Medium Priority (Enhanced Features)
- [List screens that add value but not critical]

### Low Priority (Nice to Have)
- [List screens that can be added later]

---

## Questions for AI/ML Team

After mapping, list any questions:
1. [Question about use case X]
2. [Question about API Y]
3. [Question about data format Z]

---

**Document Version:** 1.0  
**Created:** 2024-12-30  
**Status:** ⏳ Awaiting Portal Agent Input  
**Next Steps:** Portal Agent to complete mapping → AI/ML Team to review and suggest enhancements

