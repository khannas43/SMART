import React, { useState, useEffect } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import {
  Container,
  Typography,
  Box,
  Paper,
  Grid,
  Card,
  CardContent,
  CardActionArea,
  Chip,
  Tabs,
  Tab,
  TextField,
  InputAdornment,
  IconButton,
  CircularProgress,
  Alert,
  Divider,
} from '@mui/material';
import {
  Search as SearchIcon,
  Clear as ClearIcon,
  Category as SchemeIcon,
  Assignment as ApplicationIcon,
  Description as DocumentIcon,
} from '@mui/icons-material';
import { useTranslation } from 'react-i18next';
import { getSchemeName } from '@/utils/localization';
import { searchService, SearchResult } from '@/services/search.service';
import { useAppSelector } from '@/store/hooks';
import { isValidUUID } from '@/utils/uuidValidator';
import './SearchResultsPage.css';

interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

function TabPanel(props: TabPanelProps) {
  const { children, value, index, ...other } = props;
  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`search-tabpanel-${index}`}
      aria-labelledby={`search-tab-${index}`}
      {...other}
    >
      {value === index && <Box sx={{ py: 3 }}>{children}</Box>}
    </div>
  );
}

export const SearchResultsPage: React.FC = () => {
  const { t, i18n } = useTranslation();
  const navigate = useNavigate();
  const [searchParams, setSearchParams] = useSearchParams();
  const { user, isAuthenticated } = useAppSelector((state) => state.auth);

  const [query, setQuery] = useState(searchParams.get('q') || '');
  const [tabValue, setTabValue] = useState(0); // 0: All, 1: Schemes, 2: Applications, 3: Documents
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState<SearchResult | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (query.trim().length >= 2) {
      performSearch(query.trim());
    } else {
      setResults(null);
    }
  }, [query]);

  const performSearch = async (searchQuery: string) => {
    setLoading(true);
    setError(null);
    try {
      const citizenId = isAuthenticated && user?.id && isValidUUID(user.id) ? user.id : undefined;
      let searchResults: SearchResult;

      switch (tabValue) {
        case 1: // Schemes only
          searchResults = await searchService.searchSchemes(searchQuery);
          break;
        case 2: // Applications only
          if (!citizenId) {
            setError(t('search.errors.notAuthenticated', { defaultValue: 'Please log in to search applications' }));
            setLoading(false);
            return;
          }
          searchResults = await searchService.searchApplications(searchQuery, citizenId);
          break;
        case 3: // Documents only
          if (!citizenId) {
            setError(t('search.errors.notAuthenticated', { defaultValue: 'Please log in to search documents' }));
            setLoading(false);
            return;
          }
          searchResults = await searchService.searchDocuments(searchQuery, citizenId);
          break;
        default: // All
          searchResults = await searchService.searchAll(searchQuery, citizenId);
      }

      setResults(searchResults);
    } catch (err: any) {
      console.error('Search failed:', err);
      setError(err?.response?.data?.message || t('search.errors.searchFailed', { defaultValue: 'Search failed. Please try again.' }));
    } finally {
      setLoading(false);
    }
  };

  const handleQueryChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const newQuery = e.target.value;
    setQuery(newQuery);
    setSearchParams({ q: newQuery });
  };

  const handleClear = () => {
    setQuery('');
    setSearchParams({});
    setResults(null);
  };

  const handleTabChange = (_event: React.SyntheticEvent, newValue: number) => {
    setTabValue(newValue);
    if (query.trim().length >= 2) {
      performSearch(query.trim());
    }
  };

  const handleSchemeClick = (schemeId: string) => {
    navigate(`/schemes/${schemeId}`);
  };

  const handleApplicationClick = (applicationId: string) => {
    navigate(`/applications/${applicationId}`);
  };

  const handleDocumentClick = () => {
    navigate('/documents');
  };

  const renderSchemeCard = (scheme: SearchResult['schemes'][0]) => (
    <Card key={scheme.id} sx={{ height: '100%' }}>
      <CardActionArea onClick={() => handleSchemeClick(scheme.id)}>
        <CardContent>
          <Box sx={{ display: 'flex', alignItems: 'start', mb: 1 }}>
            <SchemeIcon sx={{ mr: 1, color: 'primary.main' }} />
            <Box sx={{ flexGrow: 1 }}>
              <Typography variant="h6" component="h3" gutterBottom>
                {getSchemeName(scheme, i18n.language)}
              </Typography>
              <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
                {scheme.description || scheme.category}
              </Typography>
              <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                {scheme.category && <Chip label={scheme.category} size="small" variant="outlined" />}
                {scheme.department && <Chip label={scheme.department} size="small" variant="outlined" />}
                {scheme.code && (
                  <Chip label={`Code: ${scheme.code}`} size="small" variant="outlined" color="primary" />
                )}
              </Box>
            </Box>
          </Box>
        </CardContent>
      </CardActionArea>
    </Card>
  );

  const renderApplicationCard = (app: SearchResult['applications'][0]) => (
    <Card key={app.id} sx={{ height: '100%' }}>
      <CardActionArea onClick={() => handleApplicationClick(app.id)}>
        <CardContent>
          <Box sx={{ display: 'flex', alignItems: 'start', mb: 1 }}>
            <ApplicationIcon sx={{ mr: 1, color: 'primary.main' }} />
            <Box sx={{ flexGrow: 1 }}>
              <Typography variant="h6" component="h3" gutterBottom>
                {app.applicationNumber}
              </Typography>
              <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
                {app.subject || app.serviceType}
              </Typography>
              <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                <Chip label={app.status || 'N/A'} size="small" color="primary" variant="outlined" />
                {app.schemeName && <Chip label={app.schemeName} size="small" variant="outlined" />}
              </Box>
            </Box>
          </Box>
        </CardContent>
      </CardActionArea>
    </Card>
  );

  const renderDocumentCard = (doc: SearchResult['documents'][0]) => (
    <Card key={doc.id} sx={{ height: '100%' }}>
      <CardActionArea onClick={handleDocumentClick}>
        <CardContent>
          <Box sx={{ display: 'flex', alignItems: 'start', mb: 1 }}>
            <DocumentIcon sx={{ mr: 1, color: 'primary.main' }} />
            <Box sx={{ flexGrow: 1 }}>
              <Typography variant="h6" component="h3" gutterBottom>
                {doc.fileName}
              </Typography>
              <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
                {doc.documentType}
              </Typography>
              <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                <Chip
                  label={doc.verificationStatus || 'PENDING'}
                  size="small"
                  color={doc.verificationStatus === 'VERIFIED' ? 'success' : 'default'}
                  variant="outlined"
                />
                {doc.applicationNumber && <Chip label={doc.applicationNumber} size="small" variant="outlined" />}
              </Box>
            </Box>
          </Box>
        </CardContent>
      </CardActionArea>
    </Card>
  );

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      <Typography variant="h4" component="h1" gutterBottom fontWeight="bold">
        {t('search.title', { defaultValue: 'Search Results' })}
      </Typography>

      {/* Search Bar */}
      <Paper sx={{ p: 2, mb: 3 }}>
        <TextField
          fullWidth
          placeholder={t('search.placeholder', { defaultValue: 'Search schemes, applications, documents...' })}
          value={query}
          onChange={handleQueryChange}
          InputProps={{
            startAdornment: (
              <InputAdornment position="start">
                <SearchIcon />
              </InputAdornment>
            ),
            endAdornment: (
              <InputAdornment position="end">
                {loading && <CircularProgress size={20} />}
                {query && !loading && (
                  <IconButton size="small" onClick={handleClear}>
                    <ClearIcon />
                  </IconButton>
                )}
              </InputAdornment>
            ),
          }}
        />
      </Paper>

      {error && (
        <Alert severity="error" sx={{ mb: 3 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

      {query.trim().length < 2 ? (
        <Alert severity="info">
          {t('search.enterQuery', { defaultValue: 'Enter at least 2 characters to search' })}
        </Alert>
      ) : (
        <>
          {/* Tabs */}
          <Paper sx={{ mb: 3 }}>
            <Tabs value={tabValue} onChange={handleTabChange}>
              <Tab label={t('search.all', { defaultValue: 'All' })} />
              <Tab label={t('search.schemes', { defaultValue: 'Schemes' })} />
              <Tab label={t('search.applications', { defaultValue: 'Applications' })} />
              <Tab label={t('search.documents', { defaultValue: 'Documents' })} />
            </Tabs>
          </Paper>

          {/* Results */}
          {loading ? (
            <Box sx={{ display: 'flex', justifyContent: 'center', py: 4 }}>
              <CircularProgress />
            </Box>
          ) : results && results.totalResults > 0 ? (
            <>
              <Typography variant="body1" color="text.secondary" sx={{ mb: 2 }}>
                {t('search.resultsCount', {
                  defaultValue: 'Found {{count}} results',
                  count: results.totalResults,
                })}
              </Typography>

              <TabPanel value={tabValue} index={0}>
                {/* All Results */}
                {results.schemes.length > 0 && (
                  <>
                    <Typography variant="h6" gutterBottom sx={{ mt: 2 }}>
                      {t('search.schemes', { defaultValue: 'Schemes' })} ({results.schemes.length})
                    </Typography>
                    <Grid container spacing={3} sx={{ mb: 4 }}>
                      {results.schemes.map((scheme) => (
                        <Grid item xs={12} sm={6} md={4} key={scheme.id}>
                          {renderSchemeCard(scheme)}
                        </Grid>
                      ))}
                    </Grid>
                  </>
                )}

                {results.applications.length > 0 && (
                  <>
                    {results.schemes.length > 0 && <Divider sx={{ my: 3 }} />}
                    <Typography variant="h6" gutterBottom>
                      {t('search.applications', { defaultValue: 'Applications' })} ({results.applications.length})
                    </Typography>
                    <Grid container spacing={3} sx={{ mb: 4 }}>
                      {results.applications.map((app) => (
                        <Grid item xs={12} sm={6} md={4} key={app.id}>
                          {renderApplicationCard(app)}
                        </Grid>
                      ))}
                    </Grid>
                  </>
                )}

                {results.documents.length > 0 && (
                  <>
                    {(results.schemes.length > 0 || results.applications.length > 0) && <Divider sx={{ my: 3 }} />}
                    <Typography variant="h6" gutterBottom>
                      {t('search.documents', { defaultValue: 'Documents' })} ({results.documents.length})
                    </Typography>
                    <Grid container spacing={3}>
                      {results.documents.map((doc) => (
                        <Grid item xs={12} sm={6} md={4} key={doc.id}>
                          {renderDocumentCard(doc)}
                        </Grid>
                      ))}
                    </Grid>
                  </>
                )}
              </TabPanel>

              <TabPanel value={tabValue} index={1}>
                {/* Schemes Only */}
                <Grid container spacing={3}>
                  {results.schemes.map((scheme) => (
                    <Grid item xs={12} sm={6} md={4} key={scheme.id}>
                      {renderSchemeCard(scheme)}
                    </Grid>
                  ))}
                </Grid>
              </TabPanel>

              <TabPanel value={tabValue} index={2}>
                {/* Applications Only */}
                <Grid container spacing={3}>
                  {results.applications.map((app) => (
                    <Grid item xs={12} sm={6} md={4} key={app.id}>
                      {renderApplicationCard(app)}
                    </Grid>
                  ))}
                </Grid>
              </TabPanel>

              <TabPanel value={tabValue} index={3}>
                {/* Documents Only */}
                <Grid container spacing={3}>
                  {results.documents.map((doc) => (
                    <Grid item xs={12} sm={6} md={4} key={doc.id}>
                      {renderDocumentCard(doc)}
                    </Grid>
                  ))}
                </Grid>
              </TabPanel>
            </>
          ) : (
            <Alert severity="info">
              {t('search.noResults', { defaultValue: 'No results found for your search query' })}
            </Alert>
          )}
        </>
      )}
    </Container>
  );
};

