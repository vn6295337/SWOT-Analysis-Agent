# 🎨 New React Frontend Setup

The A2A Strategy Agent now has a modern React frontend that replaces the old Streamlit dashboard.

## 🚀 Quick Start

To run the new frontend:

```bash
# Make sure you have Node.js installed (v18+ recommended)
# Install Node.js from https://nodejs.org/ if you don't have it

# Install frontend dependencies
cd frontend
npm install

# Build the frontend
npm run build

# In a separate terminal, start the FastAPI backend
cd ..
python3 api_real.py

# In another terminal, start the frontend
cd frontend
npm run preview

# Open your browser to http://localhost:4173
```

## 🎯 Using the Run Script

For convenience, use the provided script:

```bash
chmod +x run_frontend.sh
./run_frontend.sh
```

This will automatically:
1. Install dependencies
2. Build the frontend
3. Start the FastAPI backend on port 8002
4. Start the React frontend on port 4173
5. Open the application in your browser

## 🔧 Architecture

The new frontend uses:
- **React 19** with TypeScript
- **Vite** for fast development and building
- **ShadCN UI** components for professional design
- **FastAPI** backend for AI workflow processing

## 📱 Features

- Modern, responsive design
- Real-time progress tracking
- Structured SWOT analysis display
- Quality evaluation with visual indicators
- Process details and workflow visualization
- Dark/light mode toggle
- Professional UI/UX

## 🔄 Switching Between Frontends

- **New React Frontend**: `./run_frontend.sh` or `make frontend`
- **Old Streamlit Dashboard**: `streamlit run app.py` or `make ui`

## 🛠️ Development

For frontend development:

```bash
cd frontend
npm run dev
```

This starts a development server with hot reloading on port 5173.

## 📦 Building for Production

```bash
cd frontend
npm run build
```

The production build will be in the `dist/` directory.

## 🔗 API Endpoints

The frontend connects to these backend endpoints:
- `POST /analyze` - Start async analysis workflow
- `GET /workflow/{workflow_id}/status` - Get workflow status and progress
- `GET /workflow/{workflow_id}/result` - Get final workflow result
- `GET /health` - Health check

### New Architecture Features

- **Async Workflow Execution**: Workflows run in background threads
- **Real-time Polling**: Frontend polls for status updates every 700ms
- **Progress Tracking**: Shows current step, revision count, and score
- **Step Mapping**: Backend steps (Researcher, Analyst, Critic, Editor) map to UI progress