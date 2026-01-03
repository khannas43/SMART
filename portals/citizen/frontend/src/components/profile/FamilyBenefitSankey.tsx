import React from 'react';
import { Box, Typography, Paper } from '@mui/material';
import { BenefitAllocation } from '@/types/api';
import { useTranslation } from 'react-i18next';
import { getSchemeName } from '@/utils/localization';

interface FamilyBenefitSankeyProps {
  allocations: BenefitAllocation[];
}

export const FamilyBenefitSankey: React.FC<FamilyBenefitSankeyProps> = ({ allocations }) => {
  const { t, i18n } = useTranslation();
  const currentLanguage = i18n.language;
  
  // Group allocations by scheme and member
  const schemeTotals: Record<string, number> = {};
  const memberTotals: Record<string, number> = {};
  const schemeMemberMap: Record<string, Record<string, number>> = {};

  allocations.forEach((alloc) => {
    // Scheme totals
    schemeTotals[alloc.schemeId] = (schemeTotals[alloc.schemeId] || 0) + alloc.amount;
    
    // Member totals
    memberTotals[alloc.memberId] = (memberTotals[alloc.memberId] || 0) + alloc.amount;
    
    // Scheme-Member mapping
    if (!schemeMemberMap[alloc.schemeId]) {
      schemeMemberMap[alloc.schemeId] = {};
    }
    schemeMemberMap[alloc.schemeId][alloc.memberId] = 
      (schemeMemberMap[alloc.schemeId][alloc.memberId] || 0) + alloc.amount;
  });

  // Create nodes and links for Sankey diagram
  const nodes: Array<{ id: string; name: string; type: 'scheme' | 'member' }> = [];
  const links: Array<{ source: string; target: string; value: number }> = [];

  // Add scheme nodes
  Object.keys(schemeTotals).forEach((schemeId) => {
    const scheme = allocations.find((a) => a.schemeId === schemeId);
    nodes.push({
      id: `scheme-${schemeId}`,
      name: scheme?.schemeName || schemeId,
      type: 'scheme',
    });
  });

  // Add member nodes
  Object.keys(memberTotals).forEach((memberId) => {
    const member = allocations.find((a) => a.memberId === memberId);
    nodes.push({
      id: `member-${memberId}`,
      name: member?.memberName || memberId,
      type: 'member',
    });
  });

  // Add links
  Object.keys(schemeMemberMap).forEach((schemeId) => {
    Object.keys(schemeMemberMap[schemeId]).forEach((memberId) => {
      links.push({
        source: `scheme-${schemeId}`,
        target: `member-${memberId}`,
        value: schemeMemberMap[schemeId][memberId],
      });
    });
  });

  if (allocations.length === 0) {
    return (
      <Paper sx={{ p: 3, textAlign: 'center' }}>
        <Typography variant="body2" color="text.secondary">
          {t('profile.noBenefitAllocationsFound')}
        </Typography>
      </Paper>
    );
  }

  return (
    <Box>
      <Typography variant="h6" gutterBottom>
        {t('profile.familyBenefitAllocation')}
      </Typography>
      <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
        {t('profile.schemeAggregationAnalysis')}
      </Typography>
      
      {/* Simplified Sankey visualization using boxes and lines */}
      <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
        {Object.keys(schemeTotals).map((schemeId) => {
          const scheme = allocations.find((a) => a.schemeId === schemeId);
          const members = allocations.filter((a) => a.schemeId === schemeId);
          
          return (
            <Box key={schemeId} sx={{ border: '1px solid #e0e0e0', borderRadius: 1, p: 2 }}>
              <Typography variant="subtitle1" fontWeight="bold" sx={{ mb: 1 }}>
                {scheme ? getSchemeName({ name: scheme.schemeName, nameHindi: scheme.schemeNameHindi }, currentLanguage) : schemeId}
              </Typography>
              <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
                {t('profile.total')}: ₹{schemeTotals[schemeId].toLocaleString()}
              </Typography>
              <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1, mt: 1 }}>
                {members.map((member) => (
                  <Box
                    key={member.memberId}
                    sx={{
                      bgcolor: 'primary.light',
                      color: 'primary.contrastText',
                      px: 2,
                      py: 1,
                      borderRadius: 1,
                      display: 'flex',
                      alignItems: 'center',
                      gap: 1,
                    }}
                  >
                    <Typography variant="body2" fontWeight="bold">
                      {member.memberNameHindi && currentLanguage === 'hi' ? member.memberNameHindi : member.memberName}
                    </Typography>
                    <Typography variant="body2">
                      ₹{member.amount.toLocaleString()}
                    </Typography>
                  </Box>
                ))}
              </Box>
            </Box>
          );
        })}
      </Box>
    </Box>
  );
};

