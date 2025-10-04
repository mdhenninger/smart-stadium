import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import Card from '../components/UI/Card';
import Button from '../components/UI/Button';
import { storage } from '../utils';

interface SportOption {
  id: 'nfl' | 'college';
  name: string;
  fullName: string;
  icon: string;
  description: string;
  features: string[];
  stats: {
    teams: number;
    conferences?: number;
    divisions?: number;
  };
}

const SportSelection: React.FC = () => {
  const navigate = useNavigate();
  const [selectedSport, setSelectedSport] = useState<'nfl' | 'college' | null>(
    storage.get('selectedSport', null)
  );

  const sportOptions: SportOption[] = [
    {
      id: 'nfl',
      name: 'NFL',
      fullName: 'National Football League',
      icon: '🏈',
      description: 'Professional football with 32 teams across two conferences',
      features: [
        'Live game monitoring',
        'Team celebrations',
        'Real-time scores',
        'Field position tracking',
        'Playoff tracking'
      ],
      stats: {
        teams: 32,
        conferences: 2,
        divisions: 8
      }
    },
    {
      id: 'college',
      name: 'College Football',
      fullName: 'NCAA Division I FBS',
      icon: '🎓',
      description: 'College football with 130+ teams across multiple conferences',
      features: [
        'Conference tracking',
        'Rivalry celebrations',
        'Bowl game monitoring',
        'Ranking updates',
        'Championship tracking'
      ],
      stats: {
        teams: 130,
        conferences: 10
      }
    }
  ];

  const handleSportSelect = (sport: 'nfl' | 'college') => {
    setSelectedSport(sport);
    storage.set('selectedSport', sport);
  };

  const handleContinue = () => {
    if (selectedSport) {
      navigate('/games');
    }
  };

  return (
    <div className="max-w-6xl mx-auto">
      {/* Header */}
      <div className="text-center mb-8">
        <h1 className="text-4xl font-bold text-white mb-4">Select Your Sport</h1>
        <p className="text-xl text-gray-400 mb-2">
          Choose which sport you'd like to monitor for live celebrations
        </p>
        <p className="text-sm text-gray-500">
          You can change this selection anytime in settings
        </p>
      </div>

      {/* Sport Options */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
        {sportOptions.map((sport) => (
          <Card
            key={sport.id}
            clickable
            className={`transition-all duration-200 ${
              selectedSport === sport.id
                ? 'ring-2 ring-blue-500 bg-blue-900/20 border-blue-500'
                : 'hover:border-gray-600'
            }`}
            onClick={() => handleSportSelect(sport.id)}
          >
            <div className="text-center">
              {/* Icon and Title */}
              <div className="text-6xl mb-4">{sport.icon}</div>
              <h2 className="text-2xl font-bold text-white mb-2">{sport.name}</h2>
              <h3 className="text-lg text-gray-400 mb-4">{sport.fullName}</h3>
              
              {/* Description */}
              <p className="text-gray-300 mb-6 leading-relaxed">
                {sport.description}
              </p>
              
              {/* Stats */}
              <div className="flex justify-center space-x-6 mb-6">
                <div className="text-center">
                  <div className="text-2xl font-bold text-blue-400">{sport.stats.teams}</div>
                  <div className="text-xs text-gray-500">Teams</div>
                </div>
                {sport.stats.conferences && (
                  <div className="text-center">
                    <div className="text-2xl font-bold text-green-400">{sport.stats.conferences}</div>
                    <div className="text-xs text-gray-500">Conferences</div>
                  </div>
                )}
                {sport.stats.divisions && (
                  <div className="text-center">
                    <div className="text-2xl font-bold text-purple-400">{sport.stats.divisions}</div>
                    <div className="text-xs text-gray-500">Divisions</div>
                  </div>
                )}
              </div>
              
              {/* Features */}
              <div className="text-left">
                <h4 className="text-sm font-semibold text-gray-300 mb-3">Features:</h4>
                <ul className="space-y-2">
                  {sport.features.map((feature, index) => (
                    <li key={index} className="flex items-center text-sm text-gray-400">
                      <span className="text-green-400 mr-2">✓</span>
                      {feature}
                    </li>
                  ))}
                </ul>
              </div>
              
              {/* Selection Indicator */}
              {selectedSport === sport.id && (
                <div className="mt-4 flex items-center justify-center text-blue-400">
                  <span className="text-lg mr-2">✓</span>
                  <span className="font-medium">Selected</span>
                </div>
              )}
            </div>
          </Card>
        ))}
      </div>

      {/* Action Buttons */}
      <div className="flex justify-center space-x-4">
        <Button
          variant="secondary"
          size="lg"
          onClick={() => navigate('/')}
          leftIcon={<span>←</span>}
        >
          Back to Home
        </Button>
        
        <Button
          variant="primary"
          size="lg"
          onClick={handleContinue}
          disabled={!selectedSport}
          rightIcon={<span>→</span>}
        >
          Continue to Games
        </Button>
      </div>

      {/* Help Text */}
      {!selectedSport && (
        <div className="text-center mt-6">
          <p className="text-sm text-gray-500">
            Select a sport above to continue
          </p>
        </div>
      )}
    </div>
  );
};

export default SportSelection;