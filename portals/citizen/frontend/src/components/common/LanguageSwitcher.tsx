import React from 'react';
import { useTranslation } from 'react-i18next';
import { Button, ButtonGroup } from '@mui/material';
import './LanguageSwitcher.css';

const LanguageSwitcher: React.FC = () => {
  const { i18n } = useTranslation();

  const changeLanguage = (lng: string) => {
    i18n.changeLanguage(lng);
    document.documentElement.setAttribute('lang', lng);
  };

  return (
    <ButtonGroup variant="text" size="small" sx={{ border: 'none' }}>
      <Button
        onClick={() => changeLanguage('en')}
        sx={{
          fontWeight: i18n.language === 'en' ? 600 : 400,
          color: 'inherit',
          minWidth: 'auto',
          px: 1.5,
        }}
      >
        EN
      </Button>
      <Button
        onClick={() => changeLanguage('hi')}
        sx={{
          fontWeight: i18n.language === 'hi' ? 600 : 400,
          color: 'inherit',
          minWidth: 'auto',
          px: 1.5,
        }}
      >
        HI
      </Button>
    </ButtonGroup>
  );
};

export default LanguageSwitcher;

