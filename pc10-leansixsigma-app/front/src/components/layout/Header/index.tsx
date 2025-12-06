import styles from './Header.module.css';
import { useNavigate } from 'react-router-dom';

export const Header = () => {
  const navigate = useNavigate();

  return (
    <header className={styles.header}>
      <button 
        className={styles.brand}
        onClick={() => navigate('/')}
      >
        SixSigma Assistant
      </button>
      
      <button className={styles.profile}>
        Perfil / Ayuda
      </button>
    </header>
  );
};