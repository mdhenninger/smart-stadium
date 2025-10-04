import React from 'react';
import { useLocation } from 'react-router-dom';
import Header from './Header';
import Footer from './Footer';
import NavigationBar from './NavigationBar';

interface LayoutProps {
  children: React.ReactNode;
}

const Layout: React.FC<LayoutProps> = ({ children }) => {
  const location = useLocation();
  
  // Don't show navigation on the launch page
  const showNavigation = location.pathname !== '/';

  return (
    <div className="min-h-screen bg-gray-900 text-white flex flex-col">
      <Header />
      
      <div className="flex-1 flex flex-col">
        {showNavigation && <NavigationBar />}
        
        <main className="flex-1 p-4">
          {children}
        </main>
      </div>
      
      <Footer />
    </div>
  );
};

export default Layout;