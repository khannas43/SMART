import React, { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Box,
  TextField,
  InputAdornment,
  Paper,
  List,
  ListItem,
  ListItemButton,
  ListItemText,
  Typography,
  Divider,
  IconButton,
  CircularProgress,
} from '@mui/material';
import {
  Search as SearchIcon,
  Close as CloseIcon,
  Description as DocumentIcon,
  Assignment as ApplicationIcon,
  Category as SchemeIcon,
} from '@mui/icons-material';
import { useTranslation } from 'react-i18next';
import { getSchemeName } from '@/utils/localization';
import { searchService, SearchResult } from '@/services/search.service';
import { useAppSelector } from '@/store/hooks';
import { isValidUUID } from '@/utils/uuidValidator';
import './GlobalSearchBar.css';

interface GlobalSearchBarProps {
  onClose?: () => void;
}

export const GlobalSearchBar: React.FC<GlobalSearchBarProps> = ({ onClose }) => {
  const { t, i18n } = useTranslation();
  const navigate = useNavigate();
  const { user, isAuthenticated } = useAppSelector((state) => state.auth);
  const [query, setQuery] = useState('');
  const [results, setResults] = useState<SearchResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [showResults, setShowResults] = useState(false);
  const searchRef = useRef<HTMLDivElement>(null);
  const debounceTimer = useRef<NodeJS.Timeout | null>(null);

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (searchRef.current && !searchRef.current.contains(event.target as Node)) {
        setShowResults(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, []);

  useEffect(() => {
    if (debounceTimer.current) {
      clearTimeout(debounceTimer.current);
    }

    if (query.trim().length < 2) {
      setResults(null);
      setShowResults(false);
      return;
    }

    debounceTimer.current = setTimeout(() => {
      performSearch(query.trim());
    }, 300);

    return () => {
      if (debounceTimer.current) {
        clearTimeout(debounceTimer.current);
      }
    };
  }, [query]);

  const performSearch = async (searchQuery: string) => {
    setLoading(true);
    try {
      const citizenId = isAuthenticated && user?.id && isValidUUID(user.id) ? user.id : undefined;
      const searchResults = await searchService.searchAll(searchQuery, citizenId);
      setResults(searchResults);
      setShowResults(true);
    } catch (err) {
      console.error('Search failed:', err);
      setResults(null);
    } finally {
      setLoading(false);
    }
  };

  const handleQueryChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setQuery(e.target.value);
  };

  const handleClear = () => {
    setQuery('');
    setResults(null);
    setShowResults(false);
  };

  const handleSchemeClick = (schemeId: string) => {
    navigate(`/schemes/${schemeId}`);
    setShowResults(false);
    onClose?.();
  };

  const handleApplicationClick = (applicationId: string) => {
    navigate(`/applications/${applicationId}`);
    setShowResults(false);
    onClose?.();
  };

  const handleDocumentClick = (documentId: string) => {
    navigate(`/documents`);
    setShowResults(false);
    onClose?.();
  };

  const handleViewAll = () => {
    navigate(`/search?q=${encodeURIComponent(query)}`);
    setShowResults(false);
    onClose?.();
  };

  const hasResults = results && results.totalResults > 0;

  return (
    <Box ref={searchRef} sx={{ position: 'relative', width: '100%', maxWidth: 600 }}>
      <TextField
        fullWidth
        placeholder={t('search.placeholder', { defaultValue: 'Search schemes, applications, documents...' })}
        value={query}
        onChange={handleQueryChange}
        onFocus={() => query.length >= 2 && setShowResults(true)}
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
                  <CloseIcon fontSize="small" />
                </IconButton>
              )}
            </InputAdornment>
          ),
        }}
        sx={{
          '& .MuiOutlinedInput-root': {
            backgroundColor: 'rgba(255, 255, 255, 0.1)',
            '&:hover': {
              backgroundColor: 'rgba(255, 255, 255, 0.15)',
            },
            '&.Mui-focused': {
              backgroundColor: 'rgba(255, 255, 255, 0.2)',
            },
          },
          '& .MuiOutlinedInput-input': {
            color: 'white',
            '&::placeholder': {
              color: 'rgba(255, 255, 255, 0.7)',
            },
          },
        }}
      />

      {showResults && (
        <Paper
          sx={{
            position: 'absolute',
            top: '100%',
            left: 0,
            right: 0,
            mt: 1,
            maxHeight: 500,
            overflow: 'auto',
            zIndex: 1300,
            boxShadow: 3,
          }}
        >
          {loading ? (
            <Box sx={{ p: 2, textAlign: 'center' }}>
              <CircularProgress size={24} />
            </Box>
          ) : !hasResults ? (
            <Box sx={{ p: 2, textAlign: 'center' }}>
              <Typography variant="body2" color="text.secondary">
                {t('search.noResults', { defaultValue: 'No results found' })}
              </Typography>
            </Box>
          ) : (
            <>
              {results.schemes.length > 0 && (
                <>
                  <Box sx={{ p: 1, px: 2, bgcolor: 'grey.100' }}>
                    <Typography variant="caption" fontWeight="bold" color="text.secondary">
                      {t('search.schemes', { defaultValue: 'Schemes' })} ({results.schemes.length})
                    </Typography>
                  </Box>
                  <List dense>
                    {results.schemes.slice(0, 3).map((scheme) => (
                      <ListItem key={scheme.id} disablePadding>
                        <ListItemButton onClick={() => handleSchemeClick(scheme.id)}>
                          <SchemeIcon sx={{ mr: 1, color: 'primary.main' }} />
                          <ListItemText
                            primary={getSchemeName(scheme, i18n.language)}
                            secondary={scheme.description || scheme.category}
                            primaryTypographyProps={{ noWrap: true }}
                            secondaryTypographyProps={{ noWrap: true }}
                          />
                        </ListItemButton>
                      </ListItem>
                    ))}
                  </List>
                </>
              )}

              {results.applications.length > 0 && (
                <>
                  {results.schemes.length > 0 && <Divider />}
                  <Box sx={{ p: 1, px: 2, bgcolor: 'grey.100' }}>
                    <Typography variant="caption" fontWeight="bold" color="text.secondary">
                      {t('search.applications', { defaultValue: 'Applications' })} ({results.applications.length})
                    </Typography>
                  </Box>
                  <List dense>
                    {results.applications.slice(0, 3).map((app) => (
                      <ListItem key={app.id} disablePadding>
                        <ListItemButton onClick={() => handleApplicationClick(app.id)}>
                          <ApplicationIcon sx={{ mr: 1, color: 'primary.main' }} />
                          <ListItemText
                            primary={app.applicationNumber}
                            secondary={app.subject || app.serviceType}
                            primaryTypographyProps={{ noWrap: true }}
                            secondaryTypographyProps={{ noWrap: true }}
                          />
                        </ListItemButton>
                      </ListItem>
                    ))}
                  </List>
                </>
              )}

              {results.documents.length > 0 && (
                <>
                  {(results.schemes.length > 0 || results.applications.length > 0) && <Divider />}
                  <Box sx={{ p: 1, px: 2, bgcolor: 'grey.100' }}>
                    <Typography variant="caption" fontWeight="bold" color="text.secondary">
                      {t('search.documents', { defaultValue: 'Documents' })} ({results.documents.length})
                    </Typography>
                  </Box>
                  <List dense>
                    {results.documents.slice(0, 3).map((doc) => (
                      <ListItem key={doc.id} disablePadding>
                        <ListItemButton onClick={() => handleDocumentClick(doc.id)}>
                          <DocumentIcon sx={{ mr: 1, color: 'primary.main' }} />
                          <ListItemText
                            primary={doc.fileName}
                            secondary={doc.documentType}
                            primaryTypographyProps={{ noWrap: true }}
                            secondaryTypographyProps={{ noWrap: true }}
                          />
                        </ListItemButton>
                      </ListItem>
                    ))}
                  </List>
                </>
              )}

              {results.totalResults > 9 && (
                <>
                  <Divider />
                  <Box sx={{ p: 1 }}>
                    <ListItemButton onClick={handleViewAll}>
                      <ListItemText
                        primary={t('search.viewAll', { defaultValue: `View all ${results.totalResults} results` })}
                        primaryTypographyProps={{ align: 'center', color: 'primary' }}
                      />
                    </ListItemButton>
                  </Box>
                </>
              )}
            </>
          )}
        </Paper>
      )}
    </Box>
  );
};

