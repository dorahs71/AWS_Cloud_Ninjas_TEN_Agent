import React, { useState, useEffect } from 'react';
import LeopardCatSmile from '@/assets/leopard-cat-smile.gif';
import LeopardCatThink from '@/assets/leopard-cat-thinking.gif';
import LeopardCatTalk from '@/assets/leopard-cat-talking.gif';
import styles from './index.module.css';
import { rtcManager } from '@/manager';
import { ITextItem } from '@/types';

const RobotFace: React.FC = () => {
  const [currentImage, setCurrentImage] = useState(LeopardCatSmile);
  const [textState, setTextState] = useState<string>('smile');

  useEffect(() => {
    const handleTextChange = (text: ITextItem) => {
      if (!text.isFinal) {
        setTextState('thinking');
        setCurrentImage(LeopardCatThink);
      } else {
        setTextState('talking');
        setCurrentImage(LeopardCatTalk);
      }
    };

    rtcManager.on('textChanged', handleTextChange);

    return () => {
      rtcManager.off('textChanged', handleTextChange);
    };
  }, [textState]);

  useEffect(() => {
    // 當說話結束後，延遲 2 秒回到微笑狀態
    if (textState === 'talking') {
      const timer = setTimeout(() => {
        setCurrentImage(LeopardCatSmile);
        setTextState('smile');
      }, 2000);

      return () => clearTimeout(timer);
    }
  }, [textState]);

  return (
    <div className={styles.fullScreen}>
      <img 
        src={currentImage.src}
        alt="LeopardCat Animation"
        className={styles.fullScreenImage}
        loading="eager"
        decoding="async"   
      />
      <div className={styles.whiteRectangle}></div>
    </div>
  );
};

export default RobotFace;