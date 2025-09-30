# 🏟️ Smart Stadium

**Transform your space into a smart stadium that monitors game activity and presents audio visual celebrations and reactions to live events.**

## ✨ What It Does

Smart Stadium brings the excitement of professional sports venues to your home by:

- 🎯 **Real-time Game Monitoring** - Tracks live sports events from multiple sources
- 🎨 **Intelligent Celebrations** - Automatically triggers team-colored light shows for touchdowns, goals, and big plays  
- 🏈 **Multi-Sport Support** - NFL, College Football, NBA, NHL, and more
- 📱 **Smart Controls** - Web dashboard and mobile-friendly interface
- 🔴 **Red Zone Alerts** - Ambient lighting when your team enters scoring territory
- 🎉 **Victory Modes** - Special celebrations for wins and championships

## 🚀 Quick Start

```bash
# Clone the repository
git clone https://github.com/mdhenninger/smart-stadium.git
cd smart-stadium

# Install dependencies
pip install -r requirements.txt

# Configure your smart devices
cp config/stadium_config.example.json config/stadium_config.json
# Edit config file with your device IPs and preferences

# Start monitoring
python src/main.py
```

## 🎮 Supported Events

### Football (NFL & College)
- Touchdowns & Field Goals
- Red Zone Entry/Exit
- Turnovers & Sacks
- Big Plays & Defensive Stops
- Victory Celebrations

### Coming Soon
- Basketball (NBA/NCAA)
- Hockey (NHL)  
- Baseball (MLB)
- Soccer (MLS/International)

## 🔧 Compatible Devices

- **Smart Lights**: Philips Hue, WiZ Connected, LIFX
- **Audio**: Sonos, Smart Speakers (planned)
- **Displays**: Smart TVs, Projectors (planned)

## 📊 Dashboard Features

- Live game status and scores
- Manual celebration controls
- Device management
- Celebration history
- Team preferences

## 🏗️ Architecture

```
smart-stadium/
├── src/
│   ├── core/           # Celebration engine & event detection
│   ├── sports/         # Sport-specific monitoring modules  
│   ├── devices/        # Smart device controllers
│   └── main.py         # Application entry point
├── dashboard/          # Web interface
├── config/            # Configuration files
└── tests/             # Test suites
```

## 🎯 Development Status

- ✅ **NFL Monitoring** - Full support with ESPN API
- ✅ **Smart Light Control** - WiZ Connected lights tested
- ✅ **Multi-game Support** - Monitor multiple games simultaneously  
- 🚧 **Dashboard** - Web interface in development
- 🚧 **College Football** - Integration in progress
- 📋 **Other Sports** - Planned expansion

## 🤝 Contributing

We welcome contributions! Whether it's adding new sports, device support, or celebration types.

## 📄 License

MIT License - See LICENSE file for details

---

**Turn every game into a stadium experience! 🏟️⚡**