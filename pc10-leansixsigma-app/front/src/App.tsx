import { HashRouter, Routes, Route } from 'react-router-dom';
import { MainLayout } from './components/layout/MainLayout';
import { Home } from './pages/Home';
import { DefinePage } from './pages/Define';
import CostTreeApp from './pages/Tools/cost_tree';
import { ToolPage } from './pages/Tools/ToolPage';

// import { CreateProject } from './pages/Projects/CreateProject'; (La crearemos luego)

function App() {
  return (
    <HashRouter>
      <MainLayout>
          <Routes>
            
            {/* Ruta Inicial */}
            <Route path="/" element={<Home />} />
            {/* Pantalla Definir donde se verán las recomendaciones y el sidebar */}
            <Route path="/define" element={<DefinePage />} />
            {/* Herramienta Árbol de Costos */}
            <Route path="/tools/cost_tree" element={<CostTreeApp />} />
            {/* Herramientas DMAIC */}
            <Route path="/tools/:toolId" element={<ToolPage />} />
          </Routes>
      </MainLayout>
    </HashRouter>
  );
}

export default App;
