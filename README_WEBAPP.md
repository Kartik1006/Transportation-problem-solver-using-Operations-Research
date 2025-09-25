# Transportation Problem Solver - Web Application

A modern, deployable web application for solving Transportation and Assignment problems with a React/TypeScript frontend and FastAPI backend.

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Backend       │
│                 │    │                 │
│ React/TypeScript│◄──►│ FastAPI/Python  │
│ Tailwind CSS    │    │ Transport Algos │
│ Vercel Deploy   │    │ Railway Deploy  │
└─────────────────┘    └─────────────────┘
```

### Frontend (React + TypeScript + Tailwind)
- **Interactive UI** with responsive design
- **Real-time validation** and error handling
- **Step-by-step visualization** of algorithm progress
- **CSV export** functionality
- **Deployed on Vercel** for global CDN

### Backend (FastAPI + Python)
- **RESTful API** with automatic documentation
- **All original algorithms** preserved (NWCR, Least Cost, VAM, Hungarian, MODI)
- **CORS enabled** for cross-origin requests
- **Deployed on Railway** for scalable hosting

## 🚀 Features

### Transportation Problem Methods
- **NWCR** (North-West Corner Rule)
- **Least Cost Method** 
- **VAM** (Vogel's Approximation Method)
- **Row Minima** (Special Case)

### Assignment Problem
- **Hungarian Algorithm** (Optimal solution)

### Optimization
- **MODI** (Modified Distribution) for improving solutions
- **Automatic degeneracy handling**
- **Step-by-step iteration tracking**

### Modern Web Features
- **Responsive design** (mobile-friendly)
- **Real-time input validation**
- **Interactive cost matrix editing**
- **Expandable step-by-step solutions**
- **CSV export with formatted results**
- **Error handling with user-friendly messages**

## 📦 Quick Deployment

### Option 1: Deploy Both (Recommended)

1. **Deploy Backend to Railway:**
   ```bash
   cd backend
   # Push to GitHub, then connect to Railway
   # Or use Railway CLI: railway login && railway deploy
   ```

2. **Deploy Frontend to Vercel:**
   ```bash
   cd frontend
   npm run build
   # Connect GitHub repo to Vercel, auto-deploys
   ```

3. **Update API URL:**
   Set `REACT_APP_API_URL` in Vercel environment variables to your Railway backend URL.

### Option 2: Local Development

1. **Start Backend:**
   ```bash
   cd backend
   pip install -r requirements.txt
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

2. **Start Frontend:**
   ```bash
   cd frontend
   npm install
   npm start
   ```

## 📋 Deployment Guide

### Backend Deployment (Railway)

1. **Create Railway Account** at [railway.app](https://railway.app)
2. **Connect GitHub** repository
3. **Select backend folder** for deployment
4. **Railway auto-detects** Python and installs requirements
5. **Environment variables** (optional):
   ```
   PORT=8000
   PYTHONPATH=/app
   ```

### Frontend Deployment (Vercel)

1. **Create Vercel Account** at [vercel.com](https://vercel.com)
2. **Import GitHub** repository
3. **Set build settings:**
   - Framework: Create React App
   - Root Directory: `frontend`
   - Build Command: `npm run build`
   - Output Directory: `build`
4. **Environment Variables:**
   ```
   REACT_APP_API_URL=https://your-backend.railway.app
   ```

## 🛠️ Local Development

### Prerequisites
- **Node.js** 16+ and npm
- **Python** 3.8+ and pip
- **Git** for version control

### Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload
```

### Frontend Setup
```bash
cd frontend
npm install
npm start
```

### Development URLs
- **Frontend:** http://localhost:3000
- **Backend API:** http://localhost:8000
- **API Docs:** http://localhost:8000/docs

## 🔧 Configuration

### Environment Variables

**Backend (.env):**
```env
# Optional - defaults work for development
CORS_ORIGINS=*
DEBUG=true
```

**Frontend (.env):**
```env
REACT_APP_API_URL=http://localhost:8000
```

**Production Frontend:**
```env
REACT_APP_API_URL=https://your-backend-domain.railway.app
```

## 📖 API Documentation

The FastAPI backend provides automatic interactive documentation:

- **Swagger UI:** `{backend_url}/docs`
- **ReDoc:** `{backend_url}/redoc`

### Key Endpoints

- `POST /solve/transportation` - Solve transportation problems
- `POST /solve/assignment` - Solve assignment problems  
- `POST /validate/transportation` - Validate input data
- `GET /methods` - Get available solution methods
- `POST /optimize/modi` - Apply MODI optimization

## 🧪 Testing

### Backend Tests
```bash
cd backend
python -m pytest tests/  # Add tests as needed
```

### Frontend Tests
```bash
cd frontend
npm test
```

### API Testing
```bash
# Test health endpoint
curl https://your-backend.railway.app/health

# Test transportation problem
curl -X POST https://your-backend.railway.app/solve/transportation \
  -H "Content-Type: application/json" \
  -d '{
    "costs": [[8,6,10],[9,12,13],[14,7,16]], 
    "supply": [100,150,125], 
    "demand": [130,120,125],
    "method": "nwcr"
  }'
```

## 📁 Project Structure

```
D:\OR\
├── frontend/                 # React TypeScript app
│   ├── src/
│   │   ├── components/      # React components
│   │   │   ├── TransportationSolver.tsx
│   │   │   ├── AssignmentSolver.tsx
│   │   │   ├── MatrixInput.tsx
│   │   │   └── SolutionDisplay.tsx
│   │   ├── services/        # API communication
│   │   │   └── api.ts
│   │   ├── App.tsx          # Main app component
│   │   └── index.tsx        # Entry point
│   ├── public/              # Static assets
│   ├── package.json         # Dependencies
│   └── vercel.json          # Deployment config
│
├── backend/                  # FastAPI Python backend
│   ├── transport/           # Algorithm modules (unchanged)
│   │   ├── methods.py       # Transportation methods
│   │   ├── assignment.py    # Hungarian algorithm
│   │   ├── modi.py          # MODI optimization
│   │   └── utils.py         # Utility functions
│   ├── main.py              # FastAPI application
│   ├── requirements.txt     # Python dependencies
│   ├── Dockerfile           # Container config
│   └── railway.json         # Deployment config
│
└── README_WEBAPP.md         # This documentation
```

## 🚦 Status & Monitoring

### Health Checks
- **Backend:** `GET /health`
- **Frontend:** Check deployment status on Vercel dashboard
- **Railway:** Monitor logs and metrics in Railway dashboard

### Performance
- **Frontend:** Optimized build with code splitting
- **Backend:** Async FastAPI with efficient NumPy operations
- **Caching:** Browser caching for static assets

## 🔍 Troubleshooting

### Common Issues

1. **CORS Errors:**
   ```
   Error: "Access blocked by CORS policy"
   Solution: Update REACT_APP_API_URL and check backend CORS config
   ```

2. **API Connection Failed:**
   ```
   Error: "Network error - please check your connection"
   Solution: Verify backend is deployed and URL is correct
   ```

3. **Build Failures:**
   ```
   Frontend: Check Node.js version and npm install
   Backend: Check Python version and pip install requirements
   ```

### Debugging

**Backend Logs (Railway):**
```bash
# View logs in Railway dashboard or CLI
railway logs --tail
```

**Frontend Debugging:**
```bash
# Development mode with hot reload
npm start

# Build and serve locally
npm run build && npx serve -s build
```

## 🔐 Security

- **HTTPS enforced** in production
- **Input validation** on both frontend and backend
- **CORS properly configured** for production domains
- **No sensitive data** stored in client-side code

## 🎯 Performance Optimization

- **Frontend:** Code splitting, lazy loading, optimized bundle
- **Backend:** Async operations, efficient algorithms, caching headers
- **Database:** None required - stateless operation
- **CDN:** Vercel global edge network for frontend

## 📈 Scaling

- **Frontend:** Auto-scales with Vercel's global CDN
- **Backend:** Railway provides auto-scaling based on demand
- **Algorithms:** Optimized for problems up to 10×10 matrices
- **Memory:** Efficient NumPy operations for large calculations

## 🤝 Contributing

1. **Fork** the repository
2. **Create** feature branch (`git checkout -b feature/amazing-feature`)
3. **Commit** changes (`git commit -m 'Add amazing feature'`)
4. **Push** to branch (`git push origin feature/amazing-feature`)
5. **Open** Pull Request

## 📄 License

This project is open source and available under the MIT License.

## 🙏 Acknowledgments

- **Algorithms:** Classic operations research methods
- **UI Framework:** React with TypeScript
- **Styling:** Tailwind CSS for modern design
- **Icons:** Lucide React for consistent iconography
- **Deployment:** Vercel + Railway for seamless hosting

---

**Live Demo:** [https://your-app.vercel.app](https://your-app.vercel.app)  
**API Documentation:** [https://your-api.railway.app/docs](https://your-api.railway.app/docs)
