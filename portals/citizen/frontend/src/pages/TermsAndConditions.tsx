import React from 'react';
import { Link } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { Container, Typography, Box, Paper, Button } from '@mui/material';
import './TermsAndConditions.css';

const TermsAndConditions: React.FC = () => {
  const { t } = useTranslation();

  return (
    <div className="terms-conditions-page">
      <Container maxWidth="md" sx={{ py: 4 }}>
        <Box sx={{ mb: 4, textAlign: 'center' }}>
          <Typography variant="h3" component="h1" gutterBottom>
            {t('termsConditions.title')}
          </Typography>
          <Typography variant="body1" color="text.secondary">
            {t('termsConditions.subtitle')}
          </Typography>
        </Box>

        <Paper sx={{ p: 4 }}>
          <Box className="content-note" sx={{ mb: 3, p: 2, bgcolor: 'warning.light', borderRadius: 1 }}>
            <Typography variant="body2">
              <strong>Note:</strong> This content needs to be copied from{' '}
              <a
                href="https://rajasthan.gov.in/jankalyan-category-and-entry-type/0/51/88"
                target="_blank"
                rel="noopener noreferrer"
              >
                Rajasthan.gov.in Terms and Conditions page
              </a>{' '}
              and formatted appropriately.
            </Typography>
          </Box>

          <Typography variant="body1" paragraph>
            Terms and conditions content will be added here once copied from the Rajasthan.gov.in website.
          </Typography>

          <Box sx={{ mt: 4, textAlign: 'center' }}>
            <Button component={Link} to="/dashboard" variant="contained">
              {t('common.backToDashboard')}
            </Button>
          </Box>
        </Paper>
      </Container>
    </div>
  );
};

export default TermsAndConditions;

