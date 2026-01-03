import React, { useEffect, useState, useRef, useMemo, useCallback } from 'react';
import {
  Container,
  Typography,
  Box,
  Paper,
  Grid,
  CircularProgress,
  Alert,
  Card,
  CardContent,
  Tabs,
  Tab,
  Chip,
  Button,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Avatar,
  Divider,
  Tooltip,
} from '@mui/material';
import {
  Person as PersonIcon,
  FamilyRestroom as FamilyIcon,
  LocalOffer as SchemesIcon,
  Notifications as NotificationsIcon,
  Edit as EditIcon,
  VerifiedUser as VerifiedIcon,
  AccountTree as TreeIcon,
  TrendingUp as TrendingUpIcon,
  CheckCircle as CheckCircleIcon,
  Warning as WarningIcon,
  Error as ErrorIcon,
} from '@mui/icons-material';
import { useTranslation } from 'react-i18next';
import { useAppSelector, useAppDispatch } from '@/store/hooks';
import { fetchCurrentUser } from '@/store/slices/auth.slice';
import { citizenService, schemeService, notificationService, applicationService } from '@/services';
import { User, Scheme } from '@/types/api';
import { Link, useNavigate } from 'react-router-dom';
import { useMessageDialog } from '@/hooks/useMessageDialog';
import { MessageDialog } from '@/components/common/MessageDialog';
import { getUserName } from '@/utils/localization';
import ForceGraph2D from 'react-force-graph-2d';
import { FamilyBenefitSankey } from '@/components/profile/FamilyBenefitSankey';
import { ConsentToggles } from '@/components/profile/ConsentToggles';
import { AuditTimeline } from '@/components/profile/AuditTimeline';
import { MLSuggestedRelations } from '@/components/profile/MLSuggestedRelations';
import { FamilyMember, FamilyRelationship, BenefitAllocation } from '@/types/api';

interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

function TabPanel(props: TabPanelProps) {
  const { children, value, index, ...other } = props;

  const isHidden = value !== index;
  
  return (
    <div
      role="tabpanel"
      hidden={isHidden}
      id={`profile-tabpanel-${index}`}
      aria-labelledby={`profile-tab-${index}`}
      style={{ display: isHidden ? 'none' : 'block' }}
      {...other}
    >
      {value === index && <Box sx={{ py: 3 }}>{children}</Box>}
    </div>
  );
}

// Types imported from @/types/api

// Helper function to translate relationship types
const translateRelationship = (relationship: string, t: any): string => {
  const relationshipMap: Record<string, string> = {
    'Spouse': t('profile.spouse'),
    'Child': t('profile.child'),
    'Parent': t('profile.parent'),
    'Sibling': t('profile.sibling'),
    'Family Member': t('profile.familyMember'),
    'Self': t('profile.self'),
  };
  return relationshipMap[relationship] || relationship;
};

export const ProfileDashboardPage: React.FC = () => {
  const { t, i18n } = useTranslation();
  const dispatch = useAppDispatch();
  const navigate = useNavigate();
  const { user, isAuthenticated } = useAppSelector((state) => state.auth);
  const currentLanguage = i18n.language;
  const { dialog, showError, close } = useMessageDialog();

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState(0);
  const [profile, setProfile] = useState<User | null>(null);
  const [schemes, setSchemes] = useState<Scheme[]>([]);
  const [familyMembers, setFamilyMembers] = useState<FamilyMember[]>([]);
  const [familyRelationships, setFamilyRelationships] = useState<FamilyRelationship[]>([]);
  const [benefitAllocations, setBenefitAllocations] = useState<BenefitAllocation[]>([]);
  const [refreshFamilyGraph, setRefreshFamilyGraph] = useState(0);
  const graphRef = useRef<any>();
  const [pinnedNodes, setPinnedNodes] = useState<Set<string>>(new Set());

  // Store pinned node positions
  const pinnedPositions = useRef<Map<string, { fx: number; fy: number }>>(new Map());

  // Convert family data to graph format for react-force-graph-2d
  const graphData = useMemo(() => {
    if (!familyMembers || familyMembers.length === 0) {
      return { nodes: [], links: [] };
    }

    // Create nodes from family members
    const nodes = familyMembers.map((member) => {
      const pinnedPos = pinnedPositions.current.get(member.id);
      const localizedName = getUserName({ fullName: member.name, fullNameHindi: member.nameHindi }, currentLanguage);
      return {
        id: member.id,
        name: localizedName,
        originalName: member.name, // Keep original for reference
        nameHindi: member.nameHindi,
        age: member.age,
        gender: member.gender,
        relationship: member.relationship,
        confidence: member.confidence,
        isCurrentUser: member.id === user?.id,
        // Restore pinned position if node was previously pinned
        fx: pinnedPos?.fx,
        fy: pinnedPos?.fy,
      };
    });

    // Create a map for quick node lookup
    const nodeMap = new Map(nodes.map(node => [node.id, node]));

    // Create links from relationships - react-force-graph-2d can handle both IDs and node objects
    const links = familyRelationships
      .filter(rel => nodeMap.has(rel.from) && nodeMap.has(rel.to)) // Only include links where both nodes exist
      .map((rel) => ({
        source: rel.from, // Can be ID or node object
        target: rel.to,   // Can be ID or node object
        relationship: rel.relationship,
        confidence: rel.confidence,
      }));

    return { nodes, links };
  }, [familyMembers, familyRelationships, user?.id, pinnedNodes, currentLanguage]);

  useEffect(() => {
    if (!isAuthenticated) {
      setLoading(false);
      return;
    }

    if (!user?.id) {
      dispatch(fetchCurrentUser())
        .unwrap()
        .then((fetchedUser) => {
          if (fetchedUser?.id) {
            loadDashboardData();
          } else {
            setLoading(false);
          }
        })
        .catch((error) => {
          console.log('User profile not found:', error);
          setLoading(false);
        });
      return;
    }

    loadDashboardData();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [isAuthenticated, user?.id, dispatch]);

  const loadDashboardData = async () => {
    if (!user?.id) return;

    setLoading(true);
    setError(null);

    try {
      const userId = user.id;
      const isValidUUID = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i.test(userId);

      if (!isValidUUID) {
        setLoading(false);
        return;
      }

      // Load profile data
      const profileData = await citizenService.getCitizenById(userId);
      setProfile(profileData);

      // Load only enrolled schemes (schemes where user has applications)
      try {
        const applications = await applicationService.getApplicationsByCitizen(userId, 0, 100);
        const enrolledSchemeIds = new Set(
          applications.content
            .filter(app => app.schemeId)
            .map(app => app.schemeId!)
        );
        
        if (enrolledSchemeIds.size > 0) {
          // Fetch scheme details for enrolled schemes
          const schemePromises = Array.from(enrolledSchemeIds).map(schemeId =>
            schemeService.getSchemeById(schemeId).catch(() => null)
          );
          const schemeResults = await Promise.all(schemePromises);
          const enrolledSchemes = schemeResults.filter((scheme): scheme is Scheme => scheme !== null);
          setSchemes(enrolledSchemes);
        } else {
          setSchemes([]);
        }
      } catch (error) {
        console.error('Failed to load enrolled schemes:', error);
        setSchemes([]);
      }

      // Load family relationships from AI-PLATFORM-02
      try {
        const familyGraph = await citizenService.getFamilyRelationships(userId, 3);
        console.log('Family graph loaded:', familyGraph);
        
        if (familyGraph && familyGraph.members && familyGraph.members.length > 0) {
          // Check if user is already in members (by ID)
          const userInMembers = familyGraph.members.some(m => m.id === userId);
          
          if (!userInMembers) {
            // Add current user to family members if not present
            const userMember: FamilyMember = {
              id: userId,
              name: profileData.fullName || 'You',
              nameHindi: profileData.fullNameHindi,
              relationship: 'Self',
              age: profileData.dateOfBirth ? new Date().getFullYear() - new Date(profileData.dateOfBirth).getFullYear() : undefined,
              gender: profileData.gender,
              confidence: 100,
            };
            setFamilyMembers([userMember, ...familyGraph.members]);
          } else {
            setFamilyMembers(familyGraph.members);
          }
          
          setFamilyRelationships(familyGraph.relationships || []);
        } else {
          // Fallback: at least show the user
          const userMember: FamilyMember = {
            id: userId,
            name: profileData.fullName || 'You',
            nameHindi: profileData.fullNameHindi,
            relationship: 'Self',
            age: profileData.dateOfBirth ? new Date().getFullYear() - new Date(profileData.dateOfBirth).getFullYear() : undefined,
            gender: profileData.gender,
            confidence: 100,
          };
          setFamilyMembers([userMember]);
          setFamilyRelationships([]);
        }
      } catch (error) {
        console.error('Failed to load family relationships:', error);
        // Fallback to user only - still show tree view with single node
        const userMember: FamilyMember = {
          id: userId,
          name: profileData.fullName || 'You',
          nameHindi: profileData.fullNameHindi,
          relationship: 'Self',
          age: profileData.dateOfBirth ? new Date().getFullYear() - new Date(profileData.dateOfBirth).getFullYear() : undefined,
          gender: profileData.gender,
          confidence: 100,
        };
        setFamilyMembers([userMember]);
        setFamilyRelationships([]);
      }

      // Load family benefit allocations (for Sankey diagram)
      // Note: Endpoint may not exist yet, so we handle error gracefully
      try {
        const benefits = await citizenService.getFamilyBenefits(userId);
        setBenefitAllocations(benefits);
      } catch (error: any) {
        // Endpoint doesn't exist or returns 500 - handle gracefully
        console.warn('Family benefits endpoint not available:', error?.response?.status || error?.message);
        setBenefitAllocations([]);
        // Don't show error toast for this - it's optional data
      }
    } catch (err: any) {
      console.error('Error loading dashboard data:', err);
      // Only show error if it's a critical error, not for optional endpoints
      const errorMessage = err.message || 'Failed to load profile dashboard';
      // Don't show error dialog for family benefits endpoint errors (500) - it's optional
      if (!errorMessage.includes('benefits') && err?.response?.status !== 500) {
        setError(errorMessage);
        showError(errorMessage);
      } else {
        // Silently handle optional endpoint failures
        setError(null);
      }
    } finally {
      setLoading(false);
    }
  };

  // Helper functions for graph visualization
  const getNodeColor = (node: any): string => {
    if (node.isCurrentUser) return '#1976d2';
    if (node.gender === 'FEMALE') return '#FF6B9D';
    if (node.gender === 'MALE') return '#68BDF6';
    return '#95A5A6';
  };

  const getLinkColor = (link: any): string => {
    const relationship = link.relationship?.toUpperCase() || '';
    if (relationship.includes('SPOUSE')) return '#FF6B6B';
    if (relationship.includes('CHILD') || relationship.includes('PARENT')) return '#4ECDC4';
    return '#666';
  };

  const getConfidenceBadge = (confidence?: number) => {
    if (!confidence) return null;
    if (confidence >= 95) {
      return <Chip icon={<CheckCircleIcon />} label={`${confidence}%`} color="success" size="small" />;
    } else if (confidence >= 80) {
      return <Chip icon={<WarningIcon />} label={`${confidence}%`} color="warning" size="small" />;
    } else {
      return <Chip icon={<ErrorIcon />} label={`${confidence}%`} color="error" size="small" />;
    }
  };

  const handleTabChange = (_event: React.SyntheticEvent, newValue: number) => {
    setActiveTab(newValue);
  };

  if (!isAuthenticated) {
    return (
      <Container maxWidth="lg" sx={{ py: 4 }}>
        <Alert severity="warning">Please log in to view your profile dashboard</Alert>
      </Container>
    );
  }

  if (loading) {
    return (
      <Container maxWidth="lg" sx={{ py: 4, display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '50vh' }}>
        <Box sx={{ textAlign: 'center' }}>
          <CircularProgress size={60} />
          <Typography variant="body1" sx={{ mt: 2 }}>
            {t('dashboard.loadingDashboard')}
          </Typography>
        </Box>
      </Container>
    );
  }

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom fontWeight="bold">
          {t('profile.profileDashboard360View')}
        </Typography>
        <Typography variant="body1" color="text.secondary">
          {t('profile.comprehensiveView')}
        </Typography>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 3 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

      <Paper elevation={2} sx={{ mb: 3 }}>
        <Tabs 
          value={activeTab} 
          onChange={handleTabChange} 
          aria-label="profile dashboard tabs"
          indicatorColor="primary"
          textColor="primary"
        >
          <Tab label={t('profile.summary')} icon={<PersonIcon />} iconPosition="start" />
          <Tab label={t('profile.view360')} icon={<TreeIcon />} iconPosition="start" />
        </Tabs>
        {/* Debug: activeTab = {activeTab} */}
      </Paper>

      {/* Summary Tab */}
      <TabPanel value={activeTab} index={0}>
        {/* Debug: activeTab = {activeTab} */}
        <Grid container spacing={3} alignItems="flex-start">
          {/* Personal Details Card */}
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                  <Typography variant="h6" component="h2">
                    {t('profile.personalDetails')}
                  </Typography>
                  <Button
                    variant="outlined"
                    size="small"
                    startIcon={<EditIcon />}
                    onClick={() => navigate('/profile')}
                  >
                    {t('profile.editProfile')}
                  </Button>
                </Box>
                <Divider sx={{ mb: 2 }} />
                {profile && (
                  <List>
                    <ListItem>
                      <ListItemIcon>
                        <PersonIcon color="primary" />
                      </ListItemIcon>
                      <ListItemText
                        primary={t('profile.fullName')}
                        secondary={getUserName({ fullName: profile.fullName || '', fullNameHindi: profile.fullNameHindi }, currentLanguage) || t('profile.notProvided')}
                      />
                      {getConfidenceBadge(95)}
                    </ListItem>
                    <ListItem>
                      <ListItemIcon>
                        <PersonIcon color="primary" />
                      </ListItemIcon>
                      <ListItemText
                        primary={t('profile.aadhaarNumber')}
                        secondary={profile.janAadhaarId ? `${profile.janAadhaarId.substring(0, 4)} **** ****` : t('profile.notProvided')}
                      />
                      {getConfidenceBadge(98)}
                    </ListItem>
                    <ListItem>
                      <ListItemIcon>
                        <PersonIcon color="primary" />
                      </ListItemIcon>
                      <ListItemText
                        primary={t('profile.mobileNumber')}
                        secondary={profile.mobileNumber || t('profile.notProvided')}
                      />
                      {getConfidenceBadge(95)}
                    </ListItem>
                    <ListItem>
                      <ListItemIcon>
                        <PersonIcon color="primary" />
                      </ListItemIcon>
                      <ListItemText
                        primary={t('profile.email')}
                        secondary={profile.email || t('profile.notProvided')}
                      />
                      {profile.email && getConfidenceBadge(90)}
                    </ListItem>
                    <ListItem>
                      <ListItemIcon>
                        <PersonIcon color="primary" />
                      </ListItemIcon>
                      <ListItemText
                        primary={t('profile.district')}
                        secondary={profile.district || t('profile.notProvided')}
                      />
                      {profile.district && getConfidenceBadge(85)}
                    </ListItem>
                  </List>
                )}
              </CardContent>
            </Card>

            {/* Active Schemes */}
            <Box sx={{ mt: 3 }}>
              <Card>
                <CardContent>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                    <Typography variant="h6" component="h2">
                      {t('profile.activeSchemes')}
                    </Typography>
                    <Button
                      variant="text"
                      size="small"
                      component={Link}
                      to="/schemes"
                    >
                      {t('profile.viewAll')}
                    </Button>
                  </Box>
                  <Divider sx={{ mb: 2 }} />
                  {schemes.length > 0 ? (
                    <List>
                      {schemes.slice(0, 5).map((scheme) => (
                        <ListItem key={scheme.id}>
                          <ListItemIcon>
                            <SchemesIcon color="primary" />
                          </ListItemIcon>
                          <ListItemText
                            primary={scheme.name}
                            secondary={scheme.department || 'Government Scheme'}
                          />
                          <Chip label={scheme.status} color="success" size="small" />
                        </ListItem>
                      ))}
                    </List>
                  ) : (
                    <Typography variant="body2" color="text.secondary">
                      {t('profile.noActiveSchemes')}
                    </Typography>
                  )}
                </CardContent>
              </Card>
            </Box>
          </Grid>

          {/* Family Snapshot */}
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                  <Typography variant="h6" component="h2">
                    {t('profile.familySnapshot')}
                  </Typography>
                  <Button
                    variant="text"
                    size="small"
                    onClick={() => setActiveTab(1)}
                  >
                    {t('profile.view360Profile')}
                  </Button>
                </Box>
                <Divider sx={{ mb: 2 }} />
                {familyMembers.length > 0 ? (() => {
                  // Filter out current user (Self) and show all linked family members
                  const linkedMembers = familyMembers.filter(member => member.id !== user?.id && member.relationship !== 'Self');
                  return linkedMembers.length > 0 ? (
                    <Box sx={{ maxHeight: '600px', overflowY: 'auto' }}>
                      <List>
                        {linkedMembers.map((member) => (
                          <ListItem key={member.id}>
                            <ListItemIcon>
                              <Avatar sx={{ bgcolor: 'secondary.main' }}>
                                {getUserName({ fullName: member.name, fullNameHindi: member.nameHindi }, currentLanguage).charAt(0)}
                              </Avatar>
                            </ListItemIcon>
                            <ListItemText
                              primary={
                                <Link
                                  to={`/profile/family/${member.id}`}
                                  style={{
                                    textDecoration: 'none',
                                    color: '#1976d2',
                                    fontWeight: 500,
                                  }}
                                  onMouseEnter={(e) => {
                                    e.currentTarget.style.textDecoration = 'underline';
                                    e.currentTarget.style.color = '#1565c0';
                                  }}
                                  onMouseLeave={(e) => {
                                    e.currentTarget.style.textDecoration = 'none';
                                    e.currentTarget.style.color = '#1976d2';
                                  }}
                                >
                                  {getUserName({ fullName: member.name, fullNameHindi: member.nameHindi }, currentLanguage)}
                                </Link>
                              }
                              secondary={
                                <Box>
                                  <Typography variant="body2" component="span">
                                    {translateRelationship(member.relationship, t)}{member.age ? ` • ${t('profile.age')}: ${member.age}` : ''}
                                  </Typography>
                                  {member.aadhaarNumber && (
                                    <Typography variant="body2" component="span" sx={{ display: 'block', mt: 0.5, color: 'text.secondary', fontSize: '0.75rem' }}>
                                      {t('profile.aadhaarNumber')}: {member.aadhaarNumber.substring(0, 4)} **** **** {member.aadhaarNumber.substring(member.aadhaarNumber.length - 4)}
                                    </Typography>
                                  )}
                                </Box>
                              }
                            />
                            {getConfidenceBadge(member.confidence)}
                          </ListItem>
                        ))}
                      </List>
                    </Box>
                  ) : (
                    <Typography variant="body2" color="text.secondary">
                      {t('profile.noLinkedFamilyMembers')}
                    </Typography>
                  );
                })() : (
                  <Typography variant="body2" color="text.secondary">
                    {t('profile.noFamilyMembers')}
                  </Typography>
                )}
              </CardContent>
            </Card>
          </Grid>

          {/* Data Sharing Consent */}
          {user?.id && (
            <Grid item xs={12}>
              <ConsentToggles citizenId={user.id} />
            </Grid>
          )}
        </Grid>
      </TabPanel>

      {/* 360° View Tab */}
      <TabPanel value={activeTab} index={1}>
        <Grid container spacing={3}>
          {/* Family Tree Network Visualization */}
          <Grid item xs={12}>
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                  <Box>
                    <Typography variant="h6" component="h2" gutterBottom>
                      {t('profile.interactiveFamilyGraph')}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      {t('profile.visualizeFamilyRelationships')}
                    </Typography>
                    <Typography variant="caption" color="text.secondary" sx={{ mt: 0.5, display: 'block' }}>
                      {t('profile.tipDragNodes')}
                    </Typography>
                  </Box>
                </Box>
                
                {/* Relationship Type Legend */}
                <Box sx={{ mb: 2, p: 2, bgcolor: '#f5f5f5', borderRadius: 1 }}>
                  <Typography variant="subtitle2" sx={{ mb: 1, fontWeight: 'bold' }}>
                    {t('profile.relationshipTypes')}:
                  </Typography>
                  <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 2 }}>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                      <Box sx={{ width: 20, height: 3, bgcolor: '#FF6B6B', borderRadius: 1 }} />
                      <Typography variant="caption">{t('profile.spouse')}</Typography>
                    </Box>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                      <Box sx={{ width: 20, height: 3, bgcolor: '#4ECDC4', borderRadius: 1 }} />
                      <Typography variant="caption">{t('profile.childParent')}</Typography>
                    </Box>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                      <Box sx={{ width: 20, height: 3, bgcolor: '#666', borderRadius: 1 }} />
                      <Typography variant="caption">{t('profile.familyMember')}</Typography>
                    </Box>
                  </Box>
                </Box>
                
                <Divider sx={{ mb: 2 }} />
                {graphData.nodes.length > 0 ? (
                  <Box
                    sx={{
                      width: '100%',
                      height: '480px', // Reduced by 20% from 600px
                      border: '1px solid #e0e0e0',
                      borderRadius: 1,
                      backgroundColor: '#fafafa',
                      overflow: 'hidden',
                    }}
                  >
                    <ForceGraph2D
                      ref={graphRef}
                      graphData={graphData}
                      nodeLabel={(node: any) => {
                        const ageText = node.age ? ` (${t('profile.age')}: ${node.age})` : '';
                        return `${node.name}${ageText}`;
                      }}
                      nodeColor={(node: any) => getNodeColor(node)}
                      nodeVal={(node: any) => {
                        // Node size based on number of connections
                        const nodeLinks = graphData.links.filter(
                          (link: any) => {
                            const sourceId = typeof link.source === 'object' ? link.source.id : link.source;
                            const targetId = typeof link.target === 'object' ? link.target.id : link.target;
                            return sourceId === node.id || targetId === node.id;
                          }
                        );
                        return 5 + nodeLinks.length * 2;
                      }}
                      nodeCanvasObject={(node: any, ctx: CanvasRenderingContext2D, globalScale: number) => {
                        // Calculate node size (same logic as nodeVal)
                        const nodeLinks = graphData.links.filter(
                          (link: any) => {
                            const sourceId = typeof link.source === 'object' ? link.source.id : link.source;
                            const targetId = typeof link.target === 'object' ? link.target.id : link.target;
                            return sourceId === node.id || targetId === node.id;
                          }
                        );
                        const nodeSize = 5 + nodeLinks.length * 2;
                        const radius = nodeSize;
                        
                        // Draw circle with color
                        ctx.fillStyle = getNodeColor(node);
                        ctx.beginPath();
                        ctx.arc(node.x, node.y, radius, 0, 2 * Math.PI, false);
                        ctx.fill();
                        
                        // Draw border
                        ctx.strokeStyle = '#333';
                        ctx.lineWidth = 1.5 / globalScale;
                        ctx.stroke();
                        
                        // Draw name inside circle (truncate if too long)
                        const label = node.name || 'Unknown';
                        const maxLabelLength = Math.floor(radius * 0.4); // Approximate character limit
                        const displayLabel = label.length > maxLabelLength 
                          ? label.substring(0, maxLabelLength - 2) + '..' 
                          : label;
                        
                        const fontSize = Math.max(8, Math.min(11, radius * 0.7)) / globalScale;
                        ctx.font = `bold ${fontSize}px Sans-Serif`;
                        ctx.textAlign = 'center';
                        ctx.textBaseline = 'middle';
                        ctx.fillStyle = '#fff';
                        ctx.fillText(displayLabel, node.x, node.y);
                      }}
                      linkLabel={(link: any) => link.relationship || 'Relationship'}
                      linkColor={(link: any) => getLinkColor(link)}
                      linkWidth={2}
                      linkDirectionalArrowLength={6}
                      linkDirectionalArrowRelPos={1}
                      linkCurvature={0.2}
                      linkCanvasObjectMode={() => 'after'} // Render after default link rendering
                      linkCanvasObject={(link: any, ctx: CanvasRenderingContext2D, globalScale: number) => {
                        const source = typeof link.source === 'object' ? link.source : graphData.nodes.find((n: any) => n.id === link.source);
                        const target = typeof link.target === 'object' ? link.target : graphData.nodes.find((n: any) => n.id === link.target);
                        
                        if (!source || !target) return;
                        
                        // Calculate position near the arrow (slightly before the target)
                        const dx = target.x - source.x;
                        const dy = target.y - source.y;
                        const length = Math.sqrt(dx * dx + dy * dy);
                        const unitX = dx / length;
                        const unitY = dy / length;
                        
                        // Position label near the arrow head (80% along the link)
                        const labelX = source.x + unitX * length * 0.8;
                        const labelY = source.y + unitY * length * 0.8;
                        
                        // Draw relationship label
                        const label = link.relationship || 'Relationship';
                        const fontSize = 10 / globalScale;
                        ctx.font = `bold ${fontSize}px Sans-Serif`;
                        ctx.textAlign = 'center';
                        ctx.textBaseline = 'middle';
                        
                        // Draw background for text readability
                        const textWidth = ctx.measureText(label).width;
                        const padding = 4 / globalScale;
                        ctx.fillStyle = 'rgba(255, 255, 255, 0.9)';
                        ctx.fillRect(
                          labelX - textWidth / 2 - padding,
                          labelY - fontSize / 2 - padding,
                          textWidth + padding * 2,
                          fontSize + padding * 2
                        );
                        
                        // Draw text
                        ctx.fillStyle = '#333';
                        ctx.fillText(label, labelX, labelY);
                      }}
                      cooldownTicks={100}
                      onNodeHover={(node) => {
                        if (node) {
                          graphRef.current?.pauseAnimation();
                        } else {
                          graphRef.current?.resumeAnimation();
                        }
                      }}
                      onNodeDrag={(node: any) => {
                        // Update node position while dragging
                        node.fx = node.x;
                        node.fy = node.y;
                      }}
                      onNodeDragEnd={(node: any) => {
                        // Pin the node at its current position
                        node.fx = node.x;
                        node.fy = node.y;
                        // Store the pinned position
                        pinnedPositions.current.set(node.id, { fx: node.x, fy: node.y });
                        setPinnedNodes((prev) => new Set(prev).add(node.id));
                      }}
                      onNodeClick={(node: any) => {
                        if (node.id !== user?.id) {
                          navigate(`/profile/family/${node.id}`);
                        }
                      }}
                      onNodeRightClick={(node: any) => {
                        // Right-click to unpin a node
                        node.fx = undefined;
                        node.fy = undefined;
                        // Remove from pinned positions
                        pinnedPositions.current.delete(node.id);
                        setPinnedNodes((prev) => {
                          const newSet = new Set(prev);
                          newSet.delete(node.id);
                          return newSet;
                        });
                        // Restart the simulation to let the node move freely
                        graphRef.current?.resumeAnimation();
                      }}
                      width={undefined}
                      height={480} // Reduced by 20% from 600
                    />
                  </Box>
                ) : (
                  <Typography variant="body2" color="text.secondary" sx={{ textAlign: 'center', py: 4 }}>
                    {t('profile.noFamilyMembers')}
                  </Typography>
                )}
              </CardContent>
            </Card>
          </Grid>

          {/* Family Benefit Sankey Diagram */}
          <Grid item xs={12}>
            <Card>
              <CardContent>
                <FamilyBenefitSankey allocations={benefitAllocations} />
              </CardContent>
            </Card>
          </Grid>

          {/* GR Audit Timeline */}
          {user?.id && (
            <Grid item xs={12}>
              <AuditTimeline citizenId={user.id} />
            </Grid>
          )}

          {/* ML-Suggested Relations */}
          {user?.id && (
            <Grid item xs={12}>
              <MLSuggestedRelations
                citizenId={user.id}
                onRelationAccepted={() => {
                  // Refresh family graph when a relation is accepted
                  setRefreshFamilyGraph((prev) => prev + 1);
                  loadDashboardData();
                }}
              />
            </Grid>
          )}
        </Grid>
      </TabPanel>

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

