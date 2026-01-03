import React, { useState } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import {
  AppBar,
  Toolbar,
  Box,
  Button,
  IconButton,
  Badge,
  Menu,
  MenuItem,
  Avatar,
  useMediaQuery,
  useTheme,
  Drawer,
  List,
  ListItem,
  ListItemButton,
  ListItemText,
} from '@mui/material';
import MenuIcon from '@mui/icons-material/Menu';
import SearchIcon from '@mui/icons-material/Search';
import NotificationsIcon from '@mui/icons-material/Notifications';
import LanguageSwitcher from '../common/LanguageSwitcher';
import { GlobalSearchBar } from '../common/GlobalSearchBar';
import { useAppSelector, useAppDispatch } from '@/store/hooks';
import { logout } from '@/store/slices/auth.slice';
import { notificationService } from '@/services/notification.service';
import { isValidUUID } from '@/utils/uuidValidator';
import { getUserInitialsLocalized } from '@/utils/userInitials';
import './Header.css';

const Header: React.FC = () => {
  const { t, i18n } = useTranslation();
  const location = useLocation();
  const navigate = useNavigate();
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));
  const dispatch = useAppDispatch();
  const { user, isAuthenticated } = useAppSelector((state) => state.auth);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [userMenuAnchor, setUserMenuAnchor] = useState<null | HTMLElement>(null);
  const [schemesMenuAnchor, setSchemesMenuAnchor] = useState<null | HTMLElement>(null);
  const [servicesMenuAnchor, setServicesMenuAnchor] = useState<null | HTMLElement>(null);
  const [unreadNotificationCount, setUnreadNotificationCount] = useState(0);

  const handleLogout = () => {
    dispatch(logout());
    localStorage.removeItem('auth_token');
    localStorage.removeItem('refresh_token');
    navigate('/login');
    setUserMenuAnchor(null);
  };

  const isActive = (path: string) => {
    return location.pathname.startsWith(path);
  };

  // Schemes submenu
  const schemesMenuItems = [
    { path: '/schemes', label: t('menu.browseSchemes', { defaultValue: 'Browse Schemes' }) },
    { path: '/schemes/eligibility', label: t('menu.eligibilityChecker', { defaultValue: 'Eligibility Checker' }) },
  ];

  // Profile menu - direct link to dashboard (no submenu)

  // Services submenu (grouping Documents, Benefits, Payments, Services, Feedback)
  const servicesMenuItems = [
    { path: '/documents', label: t('menu.documents') },
    { path: '/benefits', label: t('menu.benefits') },
    { path: '/payments', label: t('menu.payments', { defaultValue: 'Payments' }) },
    { path: '/services', label: t('menu.services') },
    { path: '/feedback', label: t('menu.feedback', { defaultValue: 'Feedback' }) },
  ];

  const isSchemesActive = () => {
    return location.pathname.startsWith('/schemes');
  };

  const isProfileActive = () => {
    return location.pathname.startsWith('/profile');
  };

  const isServicesActive = () => {
    return (
      location.pathname.startsWith('/documents') ||
      location.pathname.startsWith('/benefits') ||
      location.pathname.startsWith('/payments') ||
      location.pathname.startsWith('/services') ||
      location.pathname.startsWith('/feedback')
    );
  };

  // Load unread notification count
  React.useEffect(() => {
    if (isAuthenticated && user?.id && isValidUUID(user.id)) {
      notificationService.getUnreadCount(user.id)
        .then((count) => setUnreadNotificationCount(count))
        .catch((err) => {
          console.error('Failed to load unread notification count:', err);
          setUnreadNotificationCount(0);
        });
    } else {
      setUnreadNotificationCount(0);
    }
  }, [isAuthenticated, user?.id]);

  return (
    <AppBar position="sticky" sx={{ zIndex: theme.zIndex.drawer + 1 }}>
      <Toolbar>
        {/* Logo */}
        <Link to="/dashboard" className="logo-link">
          <img
            src="/citizen/images/logos/smart-logo.png"
            alt={t('common.appName')}
            className="header-logo"
            height="60"
            width="auto"
          />
        </Link>

        {/* Desktop Navigation - 7 Top-Level Items */}
        {!isMobile && isAuthenticated && (
          <Box sx={{ display: 'flex', gap: 1, ml: 2, flexGrow: 1 }}>
            {/* 1. Dashboard */}
            <Button
              component={Link}
              to="/dashboard"
              color="inherit"
              sx={{
                fontWeight: isActive('/dashboard') ? 600 : 400,
                borderBottom: isActive('/dashboard') ? '2px solid' : 'none',
              }}
            >
              {t('menu.dashboard')}
            </Button>

            {/* 2. Profile (direct link to dashboard) */}
            <Button
              component={Link}
              to="/profile/dashboard"
              color="inherit"
              sx={{
                fontWeight: isProfileActive() ? 600 : 400,
                borderBottom: isProfileActive() ? '2px solid' : 'none',
              }}
            >
              {t('menu.myProfile', { defaultValue: 'Profile' })}
            </Button>

            {/* 3. Schemes (with Dropdown) */}
            <Button
              color="inherit"
              onClick={(e) => setSchemesMenuAnchor(e.currentTarget)}
              sx={{
                fontWeight: isSchemesActive() ? 600 : 400,
                borderBottom: isSchemesActive() ? '2px solid' : 'none',
              }}
            >
              {t('menu.schemes')}
            </Button>
            <Menu
              anchorEl={schemesMenuAnchor}
              open={Boolean(schemesMenuAnchor)}
              onClose={() => setSchemesMenuAnchor(null)}
            >
              {schemesMenuItems.map((item) => (
                <MenuItem
                  key={item.path}
                  onClick={() => {
                    navigate(item.path);
                    setSchemesMenuAnchor(null);
                  }}
                  selected={location.pathname === item.path || (item.path === '/schemes' && location.pathname.startsWith('/schemes') && !location.pathname.startsWith('/schemes/eligibility'))}
                >
                  {item.label}
                </MenuItem>
              ))}
            </Menu>

            {/* 4. Applications */}
            <Button
              component={Link}
              to="/applications"
              color="inherit"
              sx={{
                fontWeight: isActive('/applications') ? 600 : 400,
                borderBottom: isActive('/applications') ? '2px solid' : 'none',
              }}
            >
              {t('menu.myApplications', { defaultValue: 'Application' })}
            </Button>

            {/* 5. Services (with Dropdown - Documents, Benefits, Payments, Services, Feedback) */}
            <Button
              color="inherit"
              onClick={(e) => setServicesMenuAnchor(e.currentTarget)}
              sx={{
                fontWeight: isServicesActive() ? 600 : 400,
                borderBottom: isServicesActive() ? '2px solid' : 'none',
              }}
            >
              {t('menu.services', { defaultValue: 'Services' })}
            </Button>
            <Menu
              anchorEl={servicesMenuAnchor}
              open={Boolean(servicesMenuAnchor)}
              onClose={() => setServicesMenuAnchor(null)}
            >
              {servicesMenuItems.map((item) => (
                <MenuItem
                  key={item.path}
                  onClick={() => {
                    navigate(item.path);
                    setServicesMenuAnchor(null);
                  }}
                  selected={isActive(item.path)}
                >
                  {item.label}
                </MenuItem>
              ))}
            </Menu>

            {/* 6. Help */}
            <Button
              component={Link}
              to="/help"
              color="inherit"
              sx={{
                fontWeight: isActive('/help') ? 600 : 400,
                borderBottom: isActive('/help') ? '2px solid' : 'none',
              }}
            >
              {t('menu.helpSupport')}
            </Button>
          </Box>
        )}

        {/* Global Search Bar - Desktop */}
        {!isMobile && isAuthenticated && (
          <Box sx={{ flexGrow: 1, display: 'flex', justifyContent: 'center', mx: 2 }}>
            <GlobalSearchBar />
          </Box>
        )}

        {/* Right Side Actions */}
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, ml: 'auto' }}>
          {/* Search Icon - Mobile */}
          {isMobile && isAuthenticated && (
            <IconButton color="inherit" aria-label="search">
              <SearchIcon />
            </IconButton>
          )}

          {/* Notifications */}
          {isAuthenticated && (
            <IconButton
              component={Link}
              to="/notifications"
              color="inherit"
              aria-label="notifications"
            >
              <Badge badgeContent={unreadNotificationCount > 0 ? unreadNotificationCount : 0} color="error">
                <NotificationsIcon />
              </Badge>
            </IconButton>
          )}

          {/* Language Switcher - Desktop */}
          {!isMobile && <LanguageSwitcher />}

          {/* User Menu or Login */}
          {isAuthenticated ? (
            <>
              <IconButton
                onClick={(e) => setUserMenuAnchor(e.currentTarget)}
                sx={{ ml: 1 }}
                aria-label="user menu"
              >
                <Avatar sx={{ width: 32, height: 32 }}>
                  {getUserInitialsLocalized(user, i18n.language)}
                </Avatar>
              </IconButton>
              <Menu
                anchorEl={userMenuAnchor}
                open={Boolean(userMenuAnchor)}
                onClose={() => setUserMenuAnchor(null)}
              >
                <MenuItem onClick={() => { navigate('/settings'); setUserMenuAnchor(null); }}>
                  {t('menu.settings')}
                </MenuItem>
                <MenuItem onClick={handleLogout}>{t('buttons.logout')}</MenuItem>
              </Menu>
            </>
          ) : (
            <Button component={Link} to="/login" color="inherit">
              {t('buttons.login')}
            </Button>
          )}

          {/* Mobile Menu Button */}
          {isMobile && (
            <IconButton
              color="inherit"
              aria-label="menu"
              onClick={() => setMobileMenuOpen(true)}
            >
              <MenuIcon />
            </IconButton>
          )}
        </Box>
      </Toolbar>

      {/* Mobile Drawer */}
      <Drawer anchor="right" open={mobileMenuOpen} onClose={() => setMobileMenuOpen(false)}>
        <Box sx={{ width: 250, pt: 2 }}>
          {isAuthenticated && <LanguageSwitcher />}
          <List>
            {/* 1. Dashboard */}
            <ListItem disablePadding>
              <ListItemButton
                component={Link}
                to="/dashboard"
                selected={isActive('/dashboard')}
                onClick={() => setMobileMenuOpen(false)}
              >
                <ListItemText primary={t('menu.dashboard')} />
              </ListItemButton>
            </ListItem>

            {/* 2. Profile */}
            <ListItem disablePadding>
              <ListItemButton
                component={Link}
                to="/profile"
                selected={location.pathname === '/profile'}
                onClick={() => setMobileMenuOpen(false)}
              >
                <ListItemText primary={t('menu.myProfile', { defaultValue: 'Profile' })} />
              </ListItemButton>
            </ListItem>
            <ListItem disablePadding>
              <ListItemButton
                component={Link}
                to="/profile/dashboard"
                selected={location.pathname === '/profile/dashboard'}
                onClick={() => setMobileMenuOpen(false)}
                sx={{ pl: 4 }}
              >
                <ListItemText primary={t('menu.profileDashboard', { defaultValue: 'Profile Dashboard' })} />
              </ListItemButton>
            </ListItem>

            {/* 3. Schemes Submenu */}
            <ListItem disablePadding>
              <ListItemText primary={t('menu.schemes')} sx={{ pl: 2, fontWeight: 'bold' }} />
            </ListItem>
            {schemesMenuItems.map((item) => (
              <ListItem key={item.path} disablePadding>
                <ListItemButton
                  component={Link}
                  to={item.path}
                  selected={location.pathname === item.path || (item.path === '/schemes' && location.pathname.startsWith('/schemes') && !location.pathname.startsWith('/schemes/eligibility'))}
                  onClick={() => setMobileMenuOpen(false)}
                  sx={{ pl: 4 }}
                >
                  <ListItemText primary={item.label} />
                </ListItemButton>
              </ListItem>
            ))}

            {/* 4. Applications */}
            <ListItem disablePadding>
              <ListItemButton
                component={Link}
                to="/applications"
                selected={isActive('/applications')}
                onClick={() => setMobileMenuOpen(false)}
              >
                <ListItemText primary={t('menu.myApplications', { defaultValue: 'Application' })} />
              </ListItemButton>
            </ListItem>

            {/* 5. Services Submenu */}
            <ListItem disablePadding>
              <ListItemText primary={t('menu.services', { defaultValue: 'Services' })} sx={{ pl: 2, fontWeight: 'bold' }} />
            </ListItem>
            {servicesMenuItems.map((item) => (
              <ListItem key={item.path} disablePadding>
                <ListItemButton
                  component={Link}
                  to={item.path}
                  selected={isActive(item.path)}
                  onClick={() => setMobileMenuOpen(false)}
                  sx={{ pl: 4 }}
                >
                  <ListItemText primary={item.label} />
                </ListItemButton>
              </ListItem>
            ))}

            {/* 6. Help */}
            <ListItem disablePadding>
              <ListItemButton
                component={Link}
                to="/help"
                selected={isActive('/help')}
                onClick={() => setMobileMenuOpen(false)}
              >
                <ListItemText primary={t('menu.helpSupport')} />
              </ListItemButton>
            </ListItem>

            {isAuthenticated && (
              <ListItem disablePadding>
                <ListItemButton onClick={handleLogout}>
                  <ListItemText primary={t('buttons.logout')} />
                </ListItemButton>
              </ListItem>
            )}
          </List>
        </Box>
      </Drawer>
    </AppBar>
  );
};

export default Header;

