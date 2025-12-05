import { HashRouter, Routes, Route } from 'react-router-dom';
import { Home } from './pages/Home';
// import { CreateProject } from './pages/Projects/CreateProject'; (La crearemos luego)

function App() {
  return (
    <HashRouter>
      <Routes>
        {/* Ruta Inicial */}
        <Route path="/" element={<Home />} />
        
        {/* Futura ruta donde llegará el botón "Continuar" */}
        {/* <Route path="/projects/create" element={<CreateProject />} /> */}
      </Routes>
    </HashRouter>
  );
}

export default App;