import React, { useState, useEffect } from 'react';
import LeopardCatSmile from '@/assets/leopard-cat-smile.gif';
import LeopardCatThink from '@/assets/leopard-cat-thinking.gif';
import LeopardCatTalk from '@/assets/leopard-cat-talking.gif';
import styles from './index.module.css';
import { rtcManager } from '@/manager';
import { ITextItem } from '@/types';
import { useAppSelector } from '@/common';

const RobotFace: React.FC = () => {
  const [currentImage, setCurrentImage] = useState(LeopardCatSmile);
  const [textState, setTextState] = useState<string>('smile');
  const chatItems = useAppSelector(state => state.global.chatItems);

  useEffect(() => {
    const handleTextChange = (text: ITextItem) => {
      const lastChat = chatItems[chatItems.length - 1];
      if (!text.isFinal) {
        if (lastChat?.type === 'user') {
          setTextState('thinking');
          setCurrentImage(LeopardCatThink);
        } else if (lastChat?.type === 'agent') {
          setTextState('talking');
          setCurrentImage(LeopardCatTalk);
        }
      }
    };

    const handleRemoteUserChanged = (user: any) => {
      if (!user.audioTrack) {
        setCurrentImage(LeopardCatSmile);
        setTextState('smile');
      }
    };

    rtcManager.on('textChanged', handleTextChange);
    rtcManager.on('remoteUserChanged', handleRemoteUserChanged);

    return () => {
      rtcManager.off('textChanged', handleTextChange);
      rtcManager.off('remoteUserChanged', handleRemoteUserChanged);
    };
  }, [chatItems]);

  return (
      <div className={styles.fullScreen}>
          <div className={ styles.imageWrapper} >
            <img 
                src={currentImage.src}
                alt="LeopardCat Animation"
                className={styles.fullScreenImage}
                loading="eager"
                decoding="async"   
                    />
              </div>
      <div className={styles.whiteRectangle}></div>
    </div>
  );
};

export default RobotFace;