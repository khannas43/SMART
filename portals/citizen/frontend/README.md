# Citizen Portal - Frontend

React + TypeScript frontend application for SMART Citizen Portal.

## Tech Stack

- **React 18** - UI library
- **TypeScript** - Type safety
- **Vite** - Build tool and dev server
- **Material-UI (MUI)** - UI component library
- **React Router** - Routing
- **Redux Toolkit** - State management
- **React Query** - Data fetching and caching
- **i18next** - Internationalization
- **Axios** - HTTP client

## Getting Started

### Prerequisites

- Node.js 18+ and npm/yarn
- Backend API running (see backend README)

### Installation

```bash
# Install dependencies
npm install

# Copy environment file
cp .env.example .env

# Edit .env and configure API URL if needed
```

### Development

```bash
# Start development server
npm run dev

# Server will start on http://localhost:3000/citizen
```

### Build

```bash
# Build for production
npm run build

# Preview production build
npm run preview
```

### Testing

```bash
# Run tests
npm test

# Run tests with UI
npm run test:ui

# Run tests with coverage
npm run test:coverage
```

### Linting & Formatting

```bash
# Run ESLint
npm run lint

# Fix ESLint issues
npm run lint:fix

# Format code with Prettier
npm run format

# Check formatting
npm run format:check
```

## Project Structure

```
frontend/
├── public/              # Static assets
│   ├── images/         # Images and logos
│   └── manifest.json   # PWA manifest
├── src/
│   ├── components/     # React components
│   │   ├── common/     # Shared components
│   │   ├── layout/     # Layout components (Header, Footer)
│   │   └── features/   # Feature-specific components
│   ├── pages/          # Page components
│   ├── services/       # API services
│   ├── store/          # Redux store and slices
│   ├── hooks/          # Custom React hooks
│   ├── utils/          # Utility functions
│   ├── types/          # TypeScript type definitions
│   ├── styles/         # Global styles and theme
│   ├── i18n/           # i18next configuration
│   ├── App.tsx         # Main App component
│   └── main.tsx        # Entry point
├── package.json
├── tsconfig.json
└── vite.config.ts
```

## Environment Variables

Create a `.env` file in the frontend directory:

```env
VITE_API_BASE_URL=http://localhost:8080/citizen/api/v1
VITE_ENV=development
VITE_ENABLE_DEBUG=true
```

## Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run preview` - Preview production build
- `npm test` - Run tests
- `npm run lint` - Run ESLint
- `npm run lint:fix` - Fix ESLint issues
- `npm run format` - Format code with Prettier

## Development Guidelines

1. **Components**: Use functional components with TypeScript
2. **State Management**: Use Redux Toolkit for global state, React Query for server state
3. **Styling**: Use Material-UI components and theme
4. **Routing**: Use React Router v6
5. **API Calls**: Use Axios via service layer
6. **Internationalization**: Use i18next hooks (`useTranslation`)
7. **Type Safety**: Define types in `src/types/`

## Browser Support

- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)

## License

SMART Platform - Rajasthan Government

