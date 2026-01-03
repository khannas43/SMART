import React, { useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useNavigate } from 'react-router-dom';
import {
  Container,
  Typography,
  Box,
  Grid,
  Card,
  CardContent,
  CardActions,
  Button,
  TextField,
  InputAdornment,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  CircularProgress,
  Alert,
  Chip,
  Pagination,
  Paper,
} from '@mui/material';
import {
  Search as SearchIcon,
  LocalOffer as SchemeIcon,
  FilterList as FilterIcon,
  ArrowForward as ArrowForwardIcon,
} from '@mui/icons-material';
import { schemeService } from '@/services';
import { Scheme, PagedResponse } from '@/types/api';
import { useMessageDialog } from '@/hooks/useMessageDialog';
import { MessageDialog } from '@/components/common/MessageDialog';

import { getSchemeName, getSchemeDescription } from '@/utils/localization';
import { translateCategory, translateDepartment } from '@/utils/categoryTranslator';

const SchemesBrowsePage: React.FC = () => {
  const { t, i18n } = useTranslation();
  const navigate = useNavigate();
  const { dialog, showError, close } = useMessageDialog();

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [schemes, setSchemes] = useState<Scheme[]>([]);
  const [pagedData, setPagedData] = useState<PagedResponse<Scheme> | null>(null);

  // Filters and search
  const [searchQuery, setSearchQuery] = useState('');
  const [categoryFilter, setCategoryFilter] = useState<string>('');
  const [statusFilter, setStatusFilter] = useState<string>('ACTIVE');
  const [page, setPage] = useState(0);
  const [pageSize] = useState(12);

  // Available categories (could be fetched from API in future)
  const [categories, setCategories] = useState<string[]>([]);

  useEffect(() => {
    loadSchemes();
  }, [page, statusFilter, categoryFilter]);

  const loadSchemes = async () => {
    setLoading(true);
    setError(null);

    try {
      const data = await schemeService.getSchemes(
        page,
        pageSize,
        statusFilter || undefined,
        categoryFilter || undefined
      );

      setPagedData(data);
      setSchemes(data.content);

      // Extract unique categories from schemes
      const uniqueCategories = Array.from(
        new Set(data.content.map((s) => s.category).filter((c): c is string => !!c))
      );
      setCategories((prev) => {
        const combined = [...new Set([...prev, ...uniqueCategories])];
        return combined.sort();
      });
    } catch (err: any) {
      console.error('Error loading schemes:', err);
      const errorMessage = err.message || t('schemes.errors.loadFailed', { defaultValue: 'Failed to load schemes' });
      setError(errorMessage);
      showError(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    // Reset to first page when searching
    setPage(0);
    loadSchemes();
  };

  const handleSchemeClick = (schemeId: string) => {
    navigate(`/schemes/${schemeId}`);
  };

  const handlePageChange = (_event: React.ChangeEvent<unknown>, value: number) => {
    setPage(value - 1); // Pagination is 1-indexed, API is 0-indexed
  };

  const getStatusColor = (status: string): 'default' | 'primary' | 'secondary' | 'error' | 'info' | 'success' | 'warning' => {
    const upperStatus = status.toUpperCase();
    if (upperStatus === 'ACTIVE') return 'success';
    if (upperStatus === 'INACTIVE' || upperStatus === 'CLOSED') return 'error';
    if (upperStatus === 'UPCOMING') return 'info';
    return 'default';
  };

  // Filter schemes by search query on client side (since backend doesn't have search yet)
  const filteredSchemes = schemes.filter((scheme) => {
    if (!searchQuery) return true;
    const query = searchQuery.toLowerCase();
    const schemeName = getSchemeName(scheme, i18n.language).toLowerCase();
    const schemeDescription = getSchemeDescription(scheme, i18n.language).toLowerCase();
    return (
      schemeName.includes(query) ||
      scheme.code?.toLowerCase().includes(query) ||
      schemeDescription.includes(query) ||
      scheme.category?.toLowerCase().includes(query) ||
      scheme.department?.toLowerCase().includes(query)
    );
  });

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      {/* Header */}
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          {t('menu.browseSchemes', { defaultValue: 'Browse Schemes' })}
        </Typography>
        <Typography variant="body1" color="text.secondary">
          {t('schemes.browse.subtitle', {
            defaultValue: 'Discover and explore available government schemes',
          })}
        </Typography>
      </Box>

      {/* Search and Filters */}
      <Paper sx={{ p: 3, mb: 4 }}>
        <Grid container spacing={3} alignItems="center">
          {/* Search */}
          <Grid item xs={12} md={6}>
            <form onSubmit={handleSearch}>
              <TextField
                fullWidth
                placeholder={t('schemes.browse.searchPlaceholder', {
                  defaultValue: 'Search schemes by name, code, or description...',
                })}
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                InputProps={{
                  startAdornment: (
                    <InputAdornment position="start">
                      <SearchIcon />
                    </InputAdornment>
                  ),
                }}
              />
            </form>
          </Grid>

          {/* Category Filter */}
          <Grid item xs={12} sm={6} md={3}>
            <FormControl fullWidth>
              <InputLabel>{t('schemes.browse.category', { defaultValue: 'Category' })}</InputLabel>
              <Select
                value={categoryFilter}
                label={t('schemes.browse.category', { defaultValue: 'Category' })}
                onChange={(e) => {
                  setCategoryFilter(e.target.value);
                  setPage(0);
                }}
              >
                <MenuItem value="">
                  <em>{t('common.all', { defaultValue: 'All' })}</em>
                </MenuItem>
                {categories.map((category) => (
                  <MenuItem key={category} value={category}>
                    {translateCategory(category, i18n.language)}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </Grid>

          {/* Status Filter */}
          <Grid item xs={12} sm={6} md={3}>
            <FormControl fullWidth>
              <InputLabel>{t('schemes.browse.status', { defaultValue: 'Status' })}</InputLabel>
              <Select
                value={statusFilter}
                label={t('schemes.browse.status', { defaultValue: 'Status' })}
                onChange={(e) => {
                  setStatusFilter(e.target.value);
                  setPage(0);
                }}
              >
                <MenuItem value="ACTIVE">
                  {t('schemes.status.active', { defaultValue: 'Active' })}
                </MenuItem>
                <MenuItem value="INACTIVE">
                  {t('schemes.status.inactive', { defaultValue: 'Inactive' })}
                </MenuItem>
                <MenuItem value="UPCOMING">
                  {t('schemes.status.upcoming', { defaultValue: 'Upcoming' })}
                </MenuItem>
                <MenuItem value="">
                  <em>{t('common.all', { defaultValue: 'All' })}</em>
                </MenuItem>
              </Select>
            </FormControl>
          </Grid>
        </Grid>

        {/* Active Filters Display */}
        {(categoryFilter || statusFilter) && (
          <Box sx={{ mt: 2, display: 'flex', gap: 1, flexWrap: 'wrap', alignItems: 'center' }}>
            <FilterIcon color="action" />
            <Typography variant="body2" color="text.secondary">
              {t('schemes.browse.activeFilters', { defaultValue: 'Active filters:' })}
            </Typography>
            {categoryFilter && (
              <Chip
                label={`${t('schemes.browse.category', { defaultValue: 'Category' })}: ${translateCategory(categoryFilter, i18n.language)}`}
                onDelete={() => {
                  setCategoryFilter('');
                  setPage(0);
                }}
                size="small"
              />
            )}
            {statusFilter && (
              <Chip
                label={`${t('schemes.browse.status', { defaultValue: 'Status' })}: ${
                  statusFilter === 'ACTIVE' ? t('schemes.status.active', { defaultValue: 'Active' }) :
                  statusFilter === 'INACTIVE' ? t('schemes.status.inactive', { defaultValue: 'Inactive' }) :
                  statusFilter === 'UPCOMING' ? t('schemes.status.upcoming', { defaultValue: 'Upcoming' }) :
                  statusFilter
                }`}
                onDelete={() => {
                  setStatusFilter('ACTIVE');
                  setPage(0);
                }}
                size="small"
              />
            )}
          </Box>
        )}
      </Paper>

      {/* Error Message */}
      {error && (
        <Alert severity="error" sx={{ mb: 3 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

      {/* Loading State */}
      {loading ? (
        <Box sx={{ display: 'flex', justifyContent: 'center', py: 8 }}>
          <CircularProgress size={60} />
        </Box>
      ) : (
        <>
          {/* Schemes Grid */}
          {filteredSchemes.length > 0 ? (
            <>
              <Grid container spacing={3} sx={{ mb: 4 }}>
                {filteredSchemes.map((scheme) => (
                  <Grid item xs={12} sm={6} md={4} key={scheme.id}>
                    <Card
                      sx={{
                        height: '100%',
                        display: 'flex',
                        flexDirection: 'column',
                        transition: 'transform 0.2s, box-shadow 0.2s',
                        '&:hover': {
                          transform: 'translateY(-4px)',
                          boxShadow: 4,
                        },
                        cursor: 'pointer',
                      }}
                      onClick={() => handleSchemeClick(scheme.id)}
                    >
                      <CardContent sx={{ flexGrow: 1, position: 'relative' }}>
                        {/* Status Chip - Top Right */}
                        <Box sx={{ position: 'absolute', top: 16, right: 16 }}>
                          <Chip
                            label={
                              scheme.status === 'ACTIVE' ? t('schemes.status.active', { defaultValue: 'Active' }) :
                              scheme.status === 'INACTIVE' ? t('schemes.status.inactive', { defaultValue: 'Inactive' }) :
                              scheme.status === 'UPCOMING' ? t('schemes.status.upcoming', { defaultValue: 'Upcoming' }) :
                              scheme.status || t('schemes.status.active', { defaultValue: 'Active' })
                            }
                            color={getStatusColor(scheme.status || 'ACTIVE')}
                            size="small"
                          />
                        </Box>
                        
                        <Box sx={{ display: 'flex', alignItems: 'start', mb: 2, pr: 8 }}>
                          <SchemeIcon sx={{ fontSize: 40, color: 'primary.main', mr: 2 }} />
                          <Box sx={{ flexGrow: 1 }}>
                            <Typography variant="h6" component="h2" gutterBottom>
                              {getSchemeName(scheme, i18n.language)}
                            </Typography>
                          </Box>
                        </Box>

                        {scheme.code && (
                          <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mb: 1 }}>
                            {t('schemes.browse.code', { defaultValue: 'Code' })}: {scheme.code}
                          </Typography>
                        )}

                        {scheme.description && (
                          <Typography
                            variant="body2"
                            color="text.secondary"
                            sx={{
                              mb: 2,
                              display: '-webkit-box',
                              WebkitLineClamp: 3,
                              WebkitBoxOrient: 'vertical',
                              overflow: 'hidden',
                            }}
                          >
                            {getSchemeDescription(scheme, i18n.language)}
                          </Typography>
                        )}

                        <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1, mt: 2 }}>
                          {scheme.category && (
                            <Chip label={translateCategory(scheme.category, i18n.language)} size="small" variant="outlined" />
                          )}
                          {scheme.department && (
                            <Chip label={translateDepartment(scheme.department, i18n.language)} size="small" variant="outlined" />
                          )}
                        </Box>

                        {scheme.startDate && scheme.endDate && (
                          <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mt: 2 }}>
                            {new Date(scheme.startDate).toLocaleDateString()} -{' '}
                            {new Date(scheme.endDate).toLocaleDateString()}
                          </Typography>
                        )}
                      </CardContent>

                      <CardActions sx={{ p: 2, pt: 0 }}>
                        <Button
                          size="small"
                          endIcon={<ArrowForwardIcon />}
                          onClick={(e) => {
                            e.stopPropagation();
                            handleSchemeClick(scheme.id);
                          }}
                        >
                          {t('common.viewDetails', { defaultValue: 'View Details' })}
                        </Button>
                      </CardActions>
                    </Card>
                  </Grid>
                ))}
              </Grid>

              {/* Pagination */}
              {pagedData && pagedData.totalPages > 1 && (
                <Box sx={{ display: 'flex', justifyContent: 'center', mt: 4 }}>
                  <Pagination
                    count={pagedData.totalPages}
                    page={page + 1} // Pagination is 1-indexed
                    onChange={handlePageChange}
                    color="primary"
                    size="large"
                  />
                </Box>
              )}

              {/* Results Count */}
              <Box sx={{ textAlign: 'center', mt: 2 }}>
                <Typography variant="body2" color="text.secondary">
                  {t('schemes.browse.showing', {
                    defaultValue: 'Showing {from} to {to} of {total} schemes',
                    from: page * pageSize + 1,
                    to: Math.min((page + 1) * pageSize, pagedData?.totalElements || 0),
                    total: pagedData?.totalElements || 0,
                  })}
                </Typography>
              </Box>
            </>
          ) : (
            /* Empty State */
            <Paper sx={{ p: 6, textAlign: 'center' }}>
              <SchemeIcon sx={{ fontSize: 64, color: 'text.disabled', mb: 2 }} />
              <Typography variant="h6" gutterBottom>
                {t('schemes.browse.noSchemes', { defaultValue: 'No schemes found' })}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                {searchQuery
                  ? t('schemes.browse.noSchemesSearch', {
                      defaultValue: 'Try adjusting your search or filters',
                    })
                  : t('schemes.browse.noSchemesGeneral', {
                      defaultValue: 'No schemes are available at the moment',
                    })}
              </Typography>
              {(searchQuery || categoryFilter || statusFilter !== 'ACTIVE') && (
                <Button
                  variant="outlined"
                  sx={{ mt: 2 }}
                  onClick={() => {
                    setSearchQuery('');
                    setCategoryFilter('');
                    setStatusFilter('ACTIVE');
                    setPage(0);
                  }}
                >
                  {t('common.clearFilters', { defaultValue: 'Clear Filters' })}
                </Button>
              )}
            </Paper>
          )}
        </>
      )}

      {/* Message Dialog */}
      <MessageDialog
        open={dialog.open}
        onClose={close}
        type={dialog.type}
        message={dialog.message}
        title={dialog.title}
      />
    </Container>
  );
};

export default SchemesBrowsePage;

