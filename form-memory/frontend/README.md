# Form Memory Frontend

Modern React frontend for the Skripsi Formatter application using TypeScript, Vite, Tailwind CSS, and shadcn/ui components.

## Features

- ⚡ **Vite** - Next generation frontend tooling
- 🎨 **Tailwind CSS** - Utility-first CSS framework
- 🧩 **shadcn/ui** - High-quality React components
- 🔧 **TypeScript** - Type-safe development
- 🌍 **API Integration** - Connected to backend via Axios
- 🎯 **React Bits MCP** - Component discovery and installation

## Quick Start

### Prerequisites

- Node.js 16+ and npm/yarn
- Backend server running on `http://localhost:8000`

### Installation

```bash
npm install
```

### Development Server

```bash
npm run dev
```

Server runs on `http://localhost:5173`

### Build for Production

```bash
npm run build
```

### Add Components

Browse and install components from React Bits registry:

```bash
npx shadcn-ui add button
npx shadcn-ui add card
npx shadcn-ui add input
```

Or use the MCP server integration:

```bash
npx shadcn@latest mcp init --client vscode
```

## Project Structure

```
frontend/
├── src/
│   ├── components/      # React components
│   │   └── ui/         # shadcn/ui components
│   ├── lib/            # Utilities and API clients
│   ├── App.tsx         # Main app component
│   ├── main.tsx        # Entry point
│   └── index.css       # Global styles
├── components.json     # shadcn configuration
├── tsconfig.json       # TypeScript configuration
├── vite.config.ts      # Vite configuration
├── tailwind.config.js  # Tailwind configuration
└── index.html          # HTML entry point
```

## Configuration

### components.json

Configured with both default shadcn registry and React Bits registry:

```json
{
  "registries": {
    "@react-bits": "https://reactbits.dev/r/{name}.json",
    "default": "https://ui.shadcn.com/r"
  }
}
```

### API Configuration

Backend proxy configured in `vite.config.ts`:

```typescript
proxy: {
  '/api': {
    target: 'http://localhost:8000',
    changeOrigin: true,
    rewrite: (path) => path.replace(/^\/api/, ''),
  },
}
```

Or set `VITE_API_URL` in `.env`:

```
VITE_API_URL=http://localhost:8000
```

## Available Scripts

```bash
npm run dev          # Start development server
npm run build        # Build for production
npm run preview      # Preview production build
npm run lint         # Run ESLint
npm run type-check   # Type checking without emitting
```

## API Integration

API client available in `src/lib/api.ts`:

```typescript
import { getEnforcementStatus, enforceDocument } from '@/lib/api'

// Get system status
const status = await getEnforcementStatus()

// Upload and enforce document
const result = await enforceDocument(
  file,
  true, // include front-matter
  {
    judul: 'My Thesis',
    penulis: 'Author Name',
    nim: '20210001',
  }
)
```

## Component Development

All components are stored in `src/components/ui/` and can be added via:

```bash
npx shadcn-ui add component-name
```

Components use shadcn's composition pattern with proper TypeScript types.

## Styling

- **Tailwind CSS** - Utility classes for styling
- **CSS Variables** - Theme colors defined in `src/index.css`
- **Dark Mode** - Automatic dark mode support via `dark` class

## Browser Support

- Chrome/Edge 90+
- Firefox 88+
- Safari 14+

## Contributing

1. Create feature branches
2. Use TypeScript for type safety
3. Follow Tailwind class organization
4. Test components before committing

## License

MIT
