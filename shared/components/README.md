# Shared React Components

This directory contains reusable React components that can be used across all portals.

## Component Categories

- **UI Components**: Buttons, Inputs, Cards, Modals, etc.
- **Layout Components**: Header, Footer, Sidebar, etc.
- **Form Components**: Form fields, validators, etc.
- **Data Display**: Tables, Lists, Charts, etc.
- **Navigation**: Breadcrumbs, Menus, etc.

## Usage

Import shared components in portal code:

```typescript
import { Button, Card, Modal } from '../../../shared/components';
```

## Guidelines

- Keep components generic and reusable
- Use TypeScript for type safety
- Support multilingual (i18n)
- Make components mobile-responsive
- Follow consistent styling patterns

