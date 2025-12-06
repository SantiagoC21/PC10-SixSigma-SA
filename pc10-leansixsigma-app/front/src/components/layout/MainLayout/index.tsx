import React from 'react';
import { useLocation } from 'react-router-dom';
import { Sidebar } from '../Sidebar';
import { Header } from '../Header';

interface MainLayoutProps {
  children: React.ReactNode;
}

export const MainLayout = ({ children }: MainLayoutProps) => {
  const location = useLocation();
  
  // Lista de rutas donde NO queremos el sidebar
  const noSidebarRoutes = ['/'];

  // Verificamos si la ruta actual es el Home
  const showSidebar = !noSidebarRoutes.includes(location.pathname);

  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: '100vh', width: '100vw' }}>
      
      <Header />

      <div style={{ display: 'flex', flex: 1, overflow: 'hidden' }}>
        {showSidebar && <Sidebar />}
            <main style={{ 
                flex: 1, 
                overflowY: 'auto', 
                backgroundColor: '#fff',
                position: 'relative'
            }}>
                {children}
            </main>
      </div>
    </div>
  );
};