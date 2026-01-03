import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import {
  Container,
  Typography,
  Box,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  List,
  ListItem,
  ListItemButton,
  ListItemText,
} from '@mui/material';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import './Sitemap.css';

interface SitemapSection {
  title: string;
  links: Array<{
    label: string;
    path: string;
    description?: string;
  }>;
}

const Sitemap: React.FC = () => {
  const { t } = useTranslation();
  const [expanded, setExpanded] = useState<string | false>('dashboard');

  const handleChange = (panel: string) => (event: React.SyntheticEvent, isExpanded: boolean) => {
    setExpanded(isExpanded ? panel : false);
  };

  const sitemapSections: SitemapSection[] = [
    {
      title: t('sitemap.sections.dashboard'),
      links: [
        {
          label: t('menu.dashboard'),
          path: '/dashboard',
          description: t('sitemap.descriptions.dashboard'),
        },
      ],
    },
    {
      title: t('sitemap.sections.profile'),
      links: [
        {
          label: t('menu.profileDashboard'),
          path: '/profile/dashboard',
          description: t('sitemap.descriptions.profileDashboard'),
        },
      ],
    },
    {
      title: t('sitemap.sections.schemes'),
      links: [
        {
          label: t('menu.browseSchemes'),
          path: '/schemes',
          description: t('sitemap.descriptions.browseSchemes'),
        },
        {
          label: t('menu.eligibilityChecker'),
          path: '/schemes/eligibility',
          description: t('sitemap.descriptions.eligibilityChecker'),
        },
      ],
    },
    {
      title: t('sitemap.sections.applications'),
      links: [
        {
          label: t('menu.applicationsHub'),
          path: '/applications',
          description: t('sitemap.descriptions.applicationsHub'),
        },
        {
          label: t('application.submit.newApplication', { defaultValue: 'Submit Application' }),
          path: '/applications/submit',
          description: t('sitemap.descriptions.applicationsHub', { defaultValue: 'Submit a new application' }),
        },
      ],
    },
    {
      title: t('sitemap.sections.services'),
      links: [
        {
          label: t('menu.documents'),
          path: '/documents',
          description: t('sitemap.descriptions.documents'),
        },
        {
          label: t('menu.benefits'),
          path: '/benefits',
          description: t('sitemap.descriptions.benefitsEntitlements'),
        },
        {
          label: t('menu.payments', { defaultValue: 'Payments' }),
          path: '/payments',
          description: t('sitemap.descriptions.paymentsLedger'),
        },
        {
          label: t('menu.services'),
          path: '/services',
          description: t('sitemap.descriptions.serviceCatalog'),
        },
        {
          label: t('menu.feedback', { defaultValue: 'Feedback' }),
          path: '/feedback',
          description: t('sitemap.descriptions.helpHub', { defaultValue: 'Submit feedback and view tickets' }),
        },
      ],
    },
    {
      title: t('sitemap.sections.settings'),
      links: [
        {
          label: t('menu.notifications'),
          path: '/settings/notifications',
          description: t('sitemap.descriptions.notifications'),
        },
        {
          label: t('menu.optOutSchemes'),
          path: '/settings/opt-out',
          description: t('sitemap.descriptions.optOutSchemes'),
        },
      ],
    },
    {
      title: t('sitemap.sections.help'),
      links: [
        {
          label: t('menu.helpSupport'),
          path: '/help',
          description: t('sitemap.descriptions.helpHub'),
        },
      ],
    },
  ];

  return (
    <div className="sitemap-page">
      <Container maxWidth="md" sx={{ py: 4 }}>
        <Box sx={{ mb: 4, textAlign: 'center' }}>
          <Typography variant="h3" component="h1" gutterBottom>
            {t('sitemap.title')}
          </Typography>
          <Typography variant="body1" color="text.secondary">
            {t('sitemap.subtitle')}
          </Typography>
        </Box>

        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
          {sitemapSections.map((section, index) => (
            <Accordion
              key={index}
              expanded={expanded === `section-${index}`}
              onChange={handleChange(`section-${index}`)}
            >
              <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                <Typography variant="h6">{section.title}</Typography>
              </AccordionSummary>
              <AccordionDetails>
                <List>
                  {section.links.map((link, linkIndex) => (
                    <ListItem key={linkIndex} disablePadding>
                      <ListItemButton component={Link} to={link.path}>
                        <ListItemText
                          primary={link.label}
                          secondary={link.description}
                        />
                      </ListItemButton>
                    </ListItem>
                  ))}
                </List>
              </AccordionDetails>
            </Accordion>
          ))}
        </Box>
      </Container>
    </div>
  );
};

export default Sitemap;

