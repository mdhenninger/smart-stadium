# 🏈 Smart Stadium - Light Celebration System

**Multi-sport automated light celebrations for NFL & College football with real-time monitoring, web dashboard, and authentic team colors.**

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green.svg)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-18.0+-blue.svg)](https://reactjs.org/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.0+-blue.svg)](https://www.typescriptlang.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Buffalo Bills](https://img.shields.io/badge/Team-Buffalo%20Bills-blue.svg)](https://www.buffalobills.com/)

Transform your smart lights into the ultimate football experience! This system automatically detects scoring plays, red zone situations, sacks, turnovers, and big plays, then celebrates with synchronized light shows using authentic team colors.

## 🌟 System Overview

### **🏟️ Smart Stadium Dashboard**
- **Professional Sports UI**: Team Tracker-inspired design with live game visualization
- **6-Page Navigation Flow**: Launch → Sport Selection → Game Selection → Live Dashboard → Help → Settings
- **Real-Time Field Position**: Interactive football field showing live ball placement
- **Device Control Center**: Remote light management with celebration triggers
- **Mobile-Responsive**: Optimized for tablets, phones, and desktops

### **⚡ Multi-Sport Support**
- **🦬 NFL**: All 32 teams with official colors and priority Bills monitoring
- **🎓 College Football**: 20+ popular teams with authentic color schemes  
- **🎮 Multi-Game Monitoring**: Watch multiple games simultaneously
- **🎨 Team-Specific Colors**: Official color palettes for all supported teams

### **🌈 Complete Celebration System**
12 distinct celebration types with authentic timing:
1. **🏈 Touchdown** (30s epic celebration)
2. **🥅 Field Goal** (10s celebration)
3. **✅ Extra Point** (5s quick flash)
4. **💪 2-Point Conversion** (10s special flash)
5. **🛡️ Safety** (15s rare celebration)
6. **🏆 Victory** (60s championship celebration)
7. **🔄 Turnover** (10s defensive highlight)
8. **🏃‍♂️ Big Play** (5s for 40+ yard gains)
9. **🛡️ Defensive Stop** (5s for 4th down stops)
10. **⚡ Sack** (2s QB pressure celebration)
11. **🎯 Red Zone** (Ambient cycling - no flash)
12. **🎲 Generic Score** (Variable for unusual plays)

### **🎯 Red Zone Ambient Lighting** ⭐ *Advanced Feature*
- **Auto-Detection**: ESPN API field position integration
- **Color Cycling**: Team colors every 10 seconds with smooth fading
- **Multi-Team Support**: Priority system for overlapping red zones
- **Dynamic Transitions**: Primary → black → secondary → black

## 🚀 Quick Start

### **Prerequisites**
```bash
# Install Python dependencies
pip install -r requirements.txt

# Install frontend dependencies (for dashboard)
cd dashboard
npm install
cd ..
```

### **🎯 Start the System (2 Steps)**

**Step 1: Start Backend (Terminal 1)**
```bash
python start.py
# Or: python -m app
```

**Step 2: Start Dashboard (Terminal 2)**
```bash
cd dashboard
npm run dev
```

**Access:**
- 🌐 Dashboard: http://localhost:5173
- 📡 API: http://localhost:8000
- 📚 API Docs: http://localhost:8000/docs

### **💡 Development Tips**
```bash
# Auto-reload backend on code changes
python start.py --reload

# Custom port
python start.py --port 8080

# Allow external connections
python start.py --host 0.0.0.0

# Help
python start.py --help
```

### **🎮 Manual Testing**
```bash
# Test celebration via API
curl -X POST http://localhost:8000/api/celebrations/trigger \
  -H "Content-Type: application/json" \
  -d '{"team_abbr":"BUF","team_name":"Buffalo Bills","event_type":"touchdown"}'

# Test device connectivity
curl http://localhost:8000/api/devices/

# View all API endpoints
open http://localhost:8000/docs
```

### **📱 Dashboard Features**
- **Live Games**: Real-time scores and game status
- **Device Control**: Toggle lights, run tests
- **Manual Celebrations**: Trigger any celebration type
- **Celebration History**: View past 20 celebrations
- **WebSocket Updates**: Real-time event notifications

## 📁 Project Structure

```
smart-stadium/
├── 📁 app/                      # 🚀 Modern FastAPI Backend
│   ├── main.py                  # 🌟 FastAPI factory entry point
│   ├── __main__.py              # � Package entry (python -m app)
│   ├── dependencies.py          # � Dependency injection
│   ├── api/routes/              # 📡 REST API endpoints
│   │   ├── celebrations.py      # 🎉 Celebration triggers
│   │   ├── devices.py           # 💡 Device management
│   │   ├── games.py             # � Live game data
│   │   ├── history.py           # 📜 Event history
│   │   ├── status.py            # 📊 System status
│   │   └── teams.py             # 🏈 Team information
│   ├── core/                    # 🧠 Business logic core
│   │   ├── container.py         # 📦 Service DI container
│   │   ├── config_manager.py    # ⚙️ Configuration management
│   │   └── device_manager.py    # 🎮 Device orchestration
│   ├── models/                  # 📋 Pydantic data models
│   ├── services/                # 🔧 Business services
│   │   ├── lights_service.py    # 💡 Light control service
│   │   ├── scoreboard_service.py # 📊 ESPN integration
│   │   └── game_monitor_service.py # 🤖 Game monitoring
│   ├── websocket/               # 🔌 Real-time updates
│   │   └── manager.py           # WebSocket connection manager
│   └── utils/                   # 🛠️ Utilities
├── 📁 dashboard/                # ⚛️ React TypeScript Frontend
│   ├── src/                     # 🎨 React components
│   │   ├── api/client.ts        # � API client
│   │   ├── hooks/               # � Custom React hooks
│   │   ├── components/          # 🧩 UI components
│   │   └── types.ts             # 📋 TypeScript definitions
│   ├── vite.config.ts           # ⚡ Vite configuration
│   └── package.json             # 📦 npm dependencies
├── 📁 src/                      # 🔧 Shared modules
│   ├── devices/                 # 💡 Hardware controllers
│   │   └── smart_lights.py      # 🌈 WiZ light bridge (ACTIVE)
│   ├── sports/                  # 🏈 Sport-specific logic
│   └── core/                    # 🧠 Core utilities
├── 📁 config/                   # ⚙️ Configuration
│   ├── team_colors.json         # 🎨 Team color database
│   ├── stadium_config.json      # ⚙️ Stadium settings
│   └── celebrations.json        # � Celebration configs
├── 📁 archive/                  # 📦 Legacy code (reference only)
│   ├── legacy_backend/          # Old API implementation
│   └── legacy_scripts/          # Old CLI tools
├── 📁 College/                  # 🎓 College Football (separate)
├── 📁 tests/                    # 🧪 Unit tests
├── start.py                     # 🚀 Main launcher
├── requirements.txt             # 📦 Python dependencies
└── README.md                    # � This file
```

## 🏈 Team Support

### **NFL Teams (All 32 Teams)**
Complete support with official colors for all teams across all divisions:

**AFC East**: Bills 🦬, Dolphins, Patriots, Jets  
**AFC North**: Ravens, Bengals, Browns, Steelers  
**AFC South**: Texans, Colts, Jaguars, Titans  
**AFC West**: Broncos, Chiefs, Raiders, Chargers  
**NFC East**: Cowboys, Giants, Eagles, Commanders  
**NFC North**: Bears, Lions, Packers, Vikings  
**NFC South**: Falcons, Panthers, Saints, Buccaneers  
**NFC West**: Cardinals, Rams, 49ers, Seahawks  

### **College Teams (20+ Teams)**
Popular teams with authentic colors:
- **SEC**: Alabama, Auburn, Georgia, Florida, Tennessee, LSU
- **Big Ten**: Ohio State, Michigan, Penn State, Wisconsin
- **Big 12**: Texas, Oklahoma, Baylor, Texas Tech
- **ACC**: Clemson, Florida State, Miami, North Carolina
- **Pac-12**: USC, Oregon, Washington, Stanford
- **Independent**: Notre Dame
- **Plus more regional favorites!**

## 🔧 API & WebSocket Integration

### **🚀 FastAPI Backend**
- **REST API**: Comprehensive endpoints for celebrations, devices, teams, games
- **WebSocket Support**: Real-time bidirectional communication
- **Auto Documentation**: Interactive API docs at `/docs`
- **Production Ready**: CORS security, error handling, logging

### **📡 Key API Endpoints**

#### **Celebration Control**
- `POST /api/celebrations/trigger` - Trigger specific celebration types
- `POST /api/celebrations/stop` - Stop all ongoing celebrations
- `GET /api/celebrations/types` - List all available celebrations
- `GET /api/celebrations/status` - Current celebration status

#### **Device Management**
- `GET /api/devices` - List all connected smart lights
- `POST /api/devices/discover` - Discover new devices
- `GET /api/devices/{device_id}/status` - Individual device status
- `POST /api/devices/{device_id}/test` - Test specific device

#### **Live Game Data**
- `GET /api/games/today` - Today's games across all leagues
- `GET /api/games/live` - Currently active games with scores
- `GET /api/teams` - All supported teams with colors
- `GET /api/dashboard/data` - Complete dashboard data bundle

### **🔌 WebSocket Events**
- **Game Updates**: Live scores, field position, status changes
- **Celebration Events**: Real-time celebration triggers
- **Device Status**: Light connectivity monitoring
- **System Alerts**: Error notifications and health updates

### **📊 ESPN API Integration**
- **NFL Scoreboard**: Real-time NFL game data and statistics
- **College Scoreboard**: Live college football game monitoring
- **Game Details**: Play-by-play data for advanced detection
- **Field Position**: Red zone detection and ball placement
- **Team Information**: Official team names, colors, logos

## 🎯 Usage Examples

### **🏟️ Using the Dashboard**
1. **Start Backend**: `python start.py` (Terminal 1)
2. **Start Dashboard**: `cd dashboard && npm run dev` (Terminal 2)
3. **Access**: Open `http://localhost:5173` in browser
4. **Select Sport**: Choose NFL or College Football
5. **Pick Games**: Select which games to monitor
6. **Choose Teams**: Monitor home, away, or both teams
7. **Watch**: Automatic celebrations with authentic team colors

### **🎓 College Football (Separate System)**
The College Football module has its own implementation:
```bash
cd College
python main.py
# See College/README.md for full documentation
```

### **⚡ Advanced Play Detection**
The system automatically detects and celebrates:
- **Scoring Plays**: All touchdown, field goal, and safety types
- **Defensive Events**: Sacks, turnovers, 4th down stops
- **Big Plays**: 40+ yard non-scoring gains
- **Field Position**: Red zone entry with ambient lighting
- **Game Events**: Victory celebrations, 2-point conversions

### **🎯 Red Zone Ambient Experience**
When teams enter the red zone:
- **Auto-Detection**: ESPN field position data integration
- **Color Cycling**: Primary and secondary team colors
- **Smooth Transitions**: 10-second cycles with fade effects
- **Multi-Team Priority**: Handles overlapping red zones intelligently

## ⚙️ Configuration & Setup

### **🔌 Hardware Requirements**
- **WiZ Connected LED Smart Lights** (tested with bulbs and light strips)
- **Wi-Fi Network** - 2.4GHz or 5GHz (lights and computer on same network)
- **Minimum 1 Light** - System works with partial connectivity

### **💻 Software Requirements**
- **Python 3.8+** with pip package manager
- **Node.js 16+** for React dashboard (optional)
- **Network Discovery** - UDP broadcast for automatic light detection

### **📦 Installation**
```bash
# Clone repository
git clone <repository-url>
cd Smart_Stadium

# Install Python dependencies
pip install -r requirements.txt

# Install frontend dependencies (optional)
cd frontend
npm install

# Auto-discover lights
python -c "from src.bills_celebrations import setup_lights; setup_lights()"
```

### **🎛️ Configuration Options**

#### **Polling Speeds**
- **⚡ Ultra-Fast (5s)**: Maximum responsiveness for live action
- **🏃‍♂️ Fast (10s)**: Recommended for multi-game monitoring
- **🚶‍♂️ Normal (15s)**: Conservative and stable
- **🐌 Slow (30s)**: Original classic speed

#### **Light Settings**
- **Default State**: 2700K warm white (180 brightness)
- **Celebration Brightness**: 255 (maximum intensity)
- **Red Zone Ambient**: 200 brightness for subtle ambiance
- **Synchronization**: <1 second multi-light coordination

## 🧪 Testing & Development

### **🎮 System Testing**
```bash
# Run unit tests
pytest tests/

# Test API endpoints
curl http://localhost:8000/api/status/
curl http://localhost:8000/api/devices/

# Test celebration trigger
curl -X POST http://localhost:8000/api/celebrations/trigger \
  -H "Content-Type: application/json" \
  -d '{"team_abbr":"BUF","team_name":"Buffalo Bills","event_type":"touchdown"}'

# View API documentation
open http://localhost:8000/docs
```

### **🛠️ Development Environment**

#### **Backend Development**
```bash
# Start FastAPI with auto-reload
cd api
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Access API docs: http://localhost:8000/docs
# WebSocket test: ws://localhost:8000/ws
```

#### **Frontend Development**
```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev

# Build production bundle
npm run build:production

# Analyze bundle size
npm run analyze
```

### **📋 Testing Checklist**
- [ ] **Light Discovery**: Auto-detect all WiZ lights on network
- [ ] **API Connectivity**: Backend starts without errors
- [ ] **Dashboard Loading**: React app loads with game selection
- [ ] **WebSocket Connection**: Real-time updates working
- [ ] **Celebration Triggers**: All 12 celebration types functional
- [ ] **Multi-Game Support**: Multiple games monitored simultaneously
- [ ] **Team Colors**: Correct colors for all supported teams
- [ ] **Red Zone Detection**: Ambient lighting when teams in red zone

## 🔍 Troubleshooting

### **🔌 Light Connectivity Issues**
- **Network Check**: Ensure lights and computer on same network
- **IP Validation**: Check `config/wiz_lights_config.json` for correct IPs
- **Partial Operation**: System continues with 1+ working lights
- **Manual Discovery**: Use WiZ app to verify light network connectivity

### **📡 API & Data Issues**
- **ESPN API**: Free service with rate limits - system handles gracefully
- **Game Data**: Refresh game list if no current games found
- **WebSocket**: Dashboard reconnects automatically on connection loss
- **CORS Errors**: Ensure backend running on correct port (8000)

### **⚡ Performance Optimization**
- **Polling Speed**: Reduce frequency if experiencing lag
- **Multi-Game Limit**: Monitor fewer games for better performance
- **Network Bandwidth**: Monitor network usage during peak times
- **Device Response**: Some lights may respond slower than others

## 🚀 Production Deployment

### **🐳 Docker Deployment**
```bash
# Build backend container
cd api
docker build -t smart-stadium-api .

# Build frontend container  
cd frontend
docker build -t smart-stadium-frontend .

# Run with docker-compose
docker-compose up -d
```

### **☁️ Cloud Deployment Options**
- **Backend**: Heroku, DigitalOcean, AWS EC2, Google Cloud Run
- **Frontend**: Netlify, Vercel, GitHub Pages, AWS S3 + CloudFront
- **Environment Variables**: API keys, database URLs, CORS origins
- **SSL Certificates**: Enable HTTPS for secure WebSocket connections

## 🤝 Contributing

We welcome contributions! Here's how to get started:

1. **Fork the repository** and create your feature branch
2. **Follow code style**: Black for Python, Prettier for TypeScript
3. **Add tests**: Include unit tests for new functionality
4. **Update documentation**: Add or update relevant documentation
5. **Submit PR**: Detailed description of changes and testing

### **Development Guidelines**
- **Python**: Follow PEP 8, use type hints, async/await patterns
- **TypeScript**: Strict mode enabled, proper typing, React best practices
- **API Design**: RESTful endpoints, consistent error handling
- **Testing**: Unit tests for core functionality, integration tests for APIs

## 📄 License & Acknowledgments

**License**: MIT License - see [LICENSE](LICENSE) for details

**Special Thanks**:
- **🦬 Buffalo Bills Mafia** - The inspiration for epic celebrations
- **📊 ESPN** - Providing free real-time sports data APIs
- **💡 Philips WiZ** - Smart lighting platform that makes it all possible
- **🐍 Python Community** - asyncio, FastAPI, and networking libraries
- **⚛️ React Community** - Modern web development ecosystem

## 🔗 Resources & Links

- **[Buffalo Bills Official](https://www.buffalobills.com/)** - GO BILLS! 🦬
- **[Philips WiZ Lights](https://www.wizconnected.com/)** - Smart lighting products
- **[ESPN Developer](http://www.espn.com/apis/devcenter/)** - Sports data APIs
- **[FastAPI Docs](https://fastapi.tiangolo.com/)** - Backend framework
- **[React Docs](https://reactjs.org/)** - Frontend framework

---

## 🎉 System Status

**Current Hardware**: 3 WiZ Connected LED Lights  
**Network Status**: ✅ Auto-discovery working  
**API Health**: ✅ All endpoints operational  
**Dashboard**: ✅ React app production-ready  
**Monitoring**: ✅ NFL + College support active  

**Last Updated**: October 2025  
**Version**: Smart Stadium v2.0  

---

**🏟️ Made with ❤️ and ⚡ by Sports Fans Everywhere**

***Transform your space into a Smart Stadium - GO BILLS! 🦬***