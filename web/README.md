# Coin Classification Web App

React frontend for Indonesian coin classification with camera capture and preprocessing visualization.

## Features

- Camera capture or file upload
- Real-time preprocessing visualization (7 steps)
- Dual model comparison (CNN vs Random Forest)
- Confidence scores and processing time
- Responsive design

## Prerequisites

- Node.js 18+ and npm
- Running API server (see `../api/README.md`)

## Setup

### 1. Install Dependencies

```bash
cd web
npm install
```

### 2. Configure Environment

Copy the example environment file:

```bash
cp .env.example .env
```

Edit `.env`:

```env
# API URL - Change this to your backend server
VITE_API_URL=http://localhost:8000
```

For deployment on a home server:

```env
VITE_API_URL=http://192.168.1.100:8000
```

### 3. Run Development Server

```bash
npm run dev
```

The app will be available at `http://localhost:5173`

To allow access from other devices on the network:

```bash
npm run dev -- --host 0.0.0.0
```

### 4. Build for Production

```bash
npm run build
```

The built files will be in `dist/` directory.

## Deployment

### Option 1: Serve with Node.js

```bash
npm install -g serve
npm run build
serve -s dist -l 5173
```

### Option 2: Nginx

```nginx
server {
    listen 80;
    server_name your-domain.com;

    root /path/to/projek-edge-detection/web/dist;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }
}
```

### Option 3: Apache

Create `.htaccess` in `dist/`:

```apache
RewriteEngine On
RewriteBase /
RewriteRule ^index\.html$ - [L]
RewriteCond %{REQUEST_FILENAME} !-f
RewriteCond %{REQUEST_FILENAME} !-d
RewriteRule . /index.html [L]
```

## Project Structure

```
web/
├── src/
│   ├── App.jsx                    # Main application
│   ├── main.jsx                   # Entry point
│   ├── index.css                  # Global styles (Tailwind)
│   └── components/
│       ├── CameraCapture.jsx      # Camera/upload component
│       ├── PreprocessingSteps.jsx # 7-step visualization
│       └── PredictionResult.jsx   # Model results display
├── public/                        # Static assets
├── .env                           # Environment variables
├── .env.example                   # Example config
├── package.json
├── vite.config.js
└── tailwind.config.js
```

## Environment Variables

| Variable       | Default                 | Description     |
| -------------- | ----------------------- | --------------- |
| `VITE_API_URL` | `http://localhost:8000` | Backend API URL |

## Tech Stack

- **React 18** - UI framework
- **Vite** - Build tool
- **Tailwind CSS** - Styling
- **Lucide React** - Icons

## Troubleshooting

### Camera not working

- HTTPS is required for camera access on most browsers (except localhost)
- Check browser permissions for camera access
- Try a different browser

### API connection errors

1. Make sure the API server is running
2. Check `VITE_API_URL` in `.env` points to the correct address
3. Ensure CORS is configured on the API (see `api/.env`)

### Build errors

```bash
# Clear cache and reinstall
rm -rf node_modules
npm install
```
