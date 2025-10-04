# � College Football Support

**This directory contains the college-specific implementation of the Smart Stadium system.**

For complete documentation, setup instructions, and usage guides, please see the main [README.md](../README.md) in the project root.

## 🚀 Quick Start - College Football

### **Live Game Monitoring**
```bash
cd College/src
python college_game_monitor.py
```
*Automatically discovers live college games and allows team selection*

### **Manual Team Testing**  
```bash
cd College/src
python college_celebrations.py
```
*Test celebrations for any of 20+ supported college teams*

## � Supported Teams

**SEC**: Alabama, Auburn, Georgia, Florida, Tennessee, LSU  
**Big Ten**: Ohio State, Michigan, Penn State, Wisconsin  
**Big 12**: Texas, Oklahoma, Baylor, Texas Tech  
**ACC**: Clemson, Florida State, Miami, North Carolina  
**Pac-12**: USC, Oregon, Washington, Stanford  
**Independent**: Notre Dame  
**Plus regional favorites!**

## � Directory Structure

```
College/
├── src/
│   ├── college_celebrations.py   # College team light control
│   ├── college_game_monitor.py   # Live game monitoring
│   └── __init__.py
├── config/
│   └── wiz_lights_config.json   # Shared light configuration
├── requirements.txt             # College-specific dependencies
└── README.md                   # This file
```

## 🔗 Integration

The college system integrates seamlessly with the main Smart Stadium dashboard:

1. **🌐 Web Dashboard**: Access via main dashboard at `http://localhost:8000`
2. **🔌 Shared API**: Uses same FastAPI backend for device control
3. **💡 Same Lights**: Uses shared WiZ light configuration
4. **🎨 Team Colors**: Authentic colors for all supported teams


- ✅ Interactive game/team selection
- ✅ Complete celebration coverage

**Fire it up and test with tonight's college football action!** 🏈🎉

---

*Built for College Football Saturday nights! 🎓⚡*