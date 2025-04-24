import React from 'react';
import LeopardCatSmile from '@/assets/leopard-cat-smile.gif';
import styles from './index.module.css';

const RobotFace: React.FC = () => {
  return (
    <div className={styles.fullScreen}>
      <img 
        src={LeopardCatSmile.src}
        alt="Bmo Animation"
        className={styles.fullScreenImage}
        loading="eager"
        decoding="async"   
      />
    </div>
  );
};

export default RobotFace;