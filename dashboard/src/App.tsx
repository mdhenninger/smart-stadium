import './App.css';
import { CelebrationPanel } from './components/CelebrationPanel';
import { DevicePanel } from './components/DevicePanel';
import { GamesPanel } from './components/GamesPanel';
import { HistoryPanel } from './components/HistoryPanel';
import { LiveFeed } from './components/LiveFeed';
import { StatusBar } from './components/StatusBar';
import { useLiveEvents } from './hooks/useLiveEvents';

function App() {
  const { events, status } = useLiveEvents();

  return (
    <div className="app">
      <StatusBar connectionStatus={status} />
      <main className="app__grid">
        <section className="app__column">
          <GamesPanel />
          <CelebrationPanel />
          <HistoryPanel />
        </section>
        <section className="app__column">
          <LiveFeed events={events} />
          <DevicePanel />
        </section>
      </main>
    </div>
  );
}

export default App;
