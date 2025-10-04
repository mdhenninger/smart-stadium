import React, { useState } from 'react';
import Card from '../components/UI/Card';
import Button from '../components/UI/Button';
import Badge from '../components/UI/Badge';

interface FAQItem {
  question: string;
  answer: string;
  category: 'setup' | 'troubleshooting' | 'features' | 'api';
}

const Help: React.FC = () => {
  const [selectedCategory, setSelectedCategory] = useState<string>('all');
  const [expandedFAQ, setExpandedFAQ] = useState<number | null>(null);

  const faqItems: FAQItem[] = [
    {
      question: "How do I connect my smart lights?",
      answer: "Navigate to Settings > Devices and click 'Discover Devices'. Make sure your smart lights are on the same WiFi network and in pairing mode.",
      category: "setup"
    },
    {
      question: "Why aren't my celebrations working?",
      answer: "Check that your devices are online and discoverable. Verify that automatic celebrations are enabled in Settings and your favorite team is selected.",
      category: "troubleshooting"
    },
    {
      question: "What types of celebrations are supported?",
      answer: "We support touchdown celebrations, field goal celebrations, interceptions, fumble recoveries, sacks, big plays, game winners, and custom celebrations.",
      category: "features"
    },
    {
      question: "How do I monitor live games?",
      answer: "Select your sport, choose a live game from the game selection page, and navigate to the live dashboard to see real-time updates and celebrations.",
      category: "features"
    },
    {
      question: "The API seems to be down. What should I do?",
      answer: "Check the connection status in the header. Try refreshing the page or restarting the backend server. The API should be running on port 8000.",
      category: "troubleshooting"
    },
    {
      question: "How do I access the API documentation?",
      answer: "Visit http://localhost:8000/docs when the backend server is running to access the interactive API documentation.",
      category: "api"
    }
  ];

  const categories = [
    { id: 'all', label: 'All Topics', icon: '📚' },
    { id: 'setup', label: 'Setup', icon: '⚙️' },
    { id: 'features', label: 'Features', icon: '✨' },
    { id: 'troubleshooting', label: 'Troubleshooting', icon: '🔧' },
    { id: 'api', label: 'API', icon: '🔌' }
  ];

  const filteredFAQs = selectedCategory === 'all' 
    ? faqItems 
    : faqItems.filter(item => item.category === selectedCategory);

  const toggleFAQ = (index: number) => {
    setExpandedFAQ(expandedFAQ === index ? null : index);
  };

  return (
    <div className="max-w-6xl mx-auto">
      {/* Header */}
      <div className="text-center mb-8">
        <h1 className="text-4xl font-bold text-white mb-4">Help & Support</h1>
        <p className="text-xl text-gray-400 mb-6">
          Get help using the Smart Stadium Dashboard
        </p>
        <div className="flex justify-center space-x-4">
          <Badge variant="info">v1.0.0</Badge>
          <Badge variant="success">Online</Badge>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
        {/* Categories Sidebar */}
        <div className="lg:col-span-1">
          <Card>
            <h2 className="text-xl font-semibold mb-4">Categories</h2>
            <div className="space-y-2">
              {categories.map((category) => (
                <button
                  key={category.id}
                  onClick={() => setSelectedCategory(category.id)}
                  className={`w-full text-left p-3 rounded-lg transition-all duration-200 ${
                    selectedCategory === category.id
                      ? 'bg-blue-600 text-white'
                      : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
                  }`}
                >
                  <span className="mr-2">{category.icon}</span>
                  {category.label}
                </button>
              ))}
            </div>
          </Card>
        </div>

        {/* Main Content */}
        <div className="lg:col-span-3 space-y-8">
          {/* Quick Start Guide */}
          <Card>
            <h2 className="text-2xl font-semibold mb-6 flex items-center">
              🚀 Quick Start Guide
            </h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <h3 className="text-lg font-semibold text-white mb-3">Getting Started</h3>
                <ol className="list-decimal list-inside space-y-2 text-gray-300">
                  <li>Select your sport (NFL or College)</li>
                  <li>Choose a live game to monitor</li>
                  <li>Configure your smart lights</li>
                  <li>Set up automatic celebrations</li>
                  <li>Enjoy real-time game monitoring!</li>
                </ol>
              </div>
              <div>
                <h3 className="text-lg font-semibold text-white mb-3">Key Features</h3>
                <ul className="space-y-2 text-gray-300">
                  <li className="flex items-center">
                    <span className="text-green-400 mr-2">✓</span>
                    Live game monitoring
                  </li>
                  <li className="flex items-center">
                    <span className="text-green-400 mr-2">✓</span>
                    Smart lighting control
                  </li>
                  <li className="flex items-center">
                    <span className="text-green-400 mr-2">✓</span>
                    Automatic celebrations
                  </li>
                  <li className="flex items-center">
                    <span className="text-green-400 mr-2">✓</span>
                    Real-time dashboard
                  </li>
                  <li className="flex items-center">
                    <span className="text-green-400 mr-2">✓</span>
                    Multi-device support
                  </li>
                </ul>
              </div>
            </div>
          </Card>

          {/* System Requirements */}
          <Card>
            <h2 className="text-2xl font-semibold mb-6 flex items-center">
              💻 System Requirements
            </h2>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div>
                <h3 className="text-lg font-semibold text-white mb-3">Frontend</h3>
                <ul className="space-y-1 text-gray-300 text-sm">
                  <li>• Modern web browser</li>
                  <li>• JavaScript enabled</li>
                  <li>• Network connection</li>
                  <li>• Port 3000 accessible</li>
                </ul>
              </div>
              <div>
                <h3 className="text-lg font-semibold text-white mb-3">Backend</h3>
                <ul className="space-y-1 text-gray-300 text-sm">
                  <li>• Python 3.8+</li>
                  <li>• FastAPI server</li>
                  <li>• Port 8000 accessible</li>
                  <li>• Internet connection</li>
                </ul>
              </div>
              <div>
                <h3 className="text-lg font-semibold text-white mb-3">Smart Lights</h3>
                <ul className="space-y-1 text-gray-300 text-sm">
                  <li>• WiFi-enabled lights</li>
                  <li>• Same network</li>
                  <li>• Discoverable mode</li>
                  <li>• WiZ/LIFX/Hue support</li>
                </ul>
              </div>
            </div>
          </Card>

          {/* FAQ Section */}
          <Card>
            <h2 className="text-2xl font-semibold mb-6 flex items-center">
              ❓ Frequently Asked Questions
            </h2>
            <div className="space-y-4">
              {filteredFAQs.map((faq, index) => (
                <div key={index} className="border border-gray-700 rounded-lg">
                  <button
                    onClick={() => toggleFAQ(index)}
                    className="w-full p-4 text-left flex items-center justify-between hover:bg-gray-700 transition-colors duration-200 rounded-lg"
                  >
                    <h3 className="font-medium text-white">{faq.question}</h3>
                    <span className="text-gray-400 ml-2">
                      {expandedFAQ === index ? '−' : '+'}
                    </span>
                  </button>
                  {expandedFAQ === index && (
                    <div className="px-4 pb-4">
                      <p className="text-gray-300 leading-relaxed">{faq.answer}</p>
                    </div>
                  )}
                </div>
              ))}
            </div>
          </Card>

          {/* Contact Support */}
          <Card>
            <h2 className="text-2xl font-semibold mb-6 flex items-center">
              📞 Need More Help?
            </h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <h3 className="text-lg font-semibold text-white mb-3">Resources</h3>
                <div className="space-y-3">
                  <Button variant="ghost" size="sm" fullWidth>
                    📖 View API Documentation
                  </Button>
                  <Button variant="ghost" size="sm" fullWidth>
                    🐛 Report a Bug
                  </Button>
                  <Button variant="ghost" size="sm" fullWidth>
                    💡 Request a Feature
                  </Button>
                </div>
              </div>
              <div>
                <h3 className="text-lg font-semibold text-white mb-3">Community</h3>
                <div className="space-y-2 text-gray-300 text-sm">
                  <p>🌐 GitHub: Smart Stadium Repository</p>
                  <p>📧 Email: support@smartstadium.local</p>
                  <p>📱 Discord: Smart Stadium Community</p>
                  <p>� Twitter: @SmartStadiumApp</p>
                </div>
              </div>
            </div>
          </Card>
        </div>
      </div>
    </div>
  );
};

export default Help;