import React from 'react';
import { Link } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { Box, Container, Typography, Link as MuiLink } from '@mui/material';
import './Footer.css';

const Footer: React.FC = () => {
  const { t } = useTranslation();

  return (
    <Box
      component="footer"
      sx={{
        bgcolor: '#f5f5f5',
        borderTop: '1px solid #e0e0e0',
        py: 3,
        mt: 'auto',
      }}
    >
      <Container maxWidth="lg">
        <Box
          sx={{
            display: 'flex',
            flexDirection: { xs: 'column', sm: 'row' },
            justifyContent: 'center',
            alignItems: 'center',
            gap: 2,
          }}
        >
          {/* Footer Links */}
          <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap', justifyContent: 'center' }}>
            <MuiLink component={Link} to="/terms-conditions" color="primary" underline="hover">
              {t('footer.termsConditions')}
            </MuiLink>
            <Typography component="span" color="text.secondary">
              |
            </Typography>
            <MuiLink component={Link} to="/sitemap" color="primary" underline="hover">
              {t('footer.sitemap')}
            </MuiLink>
            <Typography component="span" color="text.secondary">
              |
            </Typography>
            <MuiLink
              href="https://rajasthan.gov.in/pages/website-policies"
              target="_blank"
              rel="noopener noreferrer"
              color="primary"
              underline="hover"
            >
              {t('footer.websitePolicy')}
              <Typography component="span" sx={{ ml: 0.5, fontSize: '0.75rem' }}>
                ↗
              </Typography>
            </MuiLink>
          </Box>
        </Box>

        {/* Copyright */}
        <Box sx={{ mt: 2, textAlign: 'center' }}>
          <Typography variant="body2" color="text.secondary">
            {t('footer.copyright', { year: 2026 })}
          </Typography>
        </Box>
      </Container>
    </Box>
  );
};

export default Footer;

