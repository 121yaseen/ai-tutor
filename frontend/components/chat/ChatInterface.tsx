import React from 'react';
import { useAuth } from '@/hooks/useAuth';
import { useChatSession } from '@/hooks/useChatSession';
import VoiceVisualizer from './VoiceVisualizer';
import styles from '../../styles/ChatInterface.module.css';

const ChatInterface = () => {
    const { logout } = useAuth();
    const { 
        isSessionActive, 
        conversation, 
        startSession, 
        stopSession, 
        analyser,
        isThinking,
        isSpeaking
    } = useChatSession();

    const getGreeting = () => {
        const hour = new Date().getHours();
        if (hour < 12) return 'Good Morning';
        if (hour < 18) return 'Good Afternoon';
        return 'Good Evening';
    };

    return (
        <div className={styles.chatContainer}>
            <button onClick={logout} className={styles.logoutButton}>Logout</button>
            
            <div className={styles.conversationContainer}>
                {conversation.map((message, index) => (
                    <div key={index} className={`${styles.message} ${styles[message.role]}`}>
                        <span className={styles.messageRole}>{message.role === 'user' ? 'You' : 'Pistah'}</span>
                        <p>{message.content}</p>
                    </div>
                ))}
                {isThinking && (
                     <div className={`${styles.message} ${styles.assistant}`}>
                        <span className={styles.messageRole}>Pistah</span>
                        <div className={styles.thinkingIndicator}>
                            <span></span><span></span><span></span>
                        </div>
                    </div>
                )}
            </div>

            <div className={styles.controlsContainer}>
                <div className={styles.visualizerWrapper}>
                    <VoiceVisualizer analyser={analyser} isActive={isSessionActive} />
                    {!isSessionActive && (
                        <div className={styles.introText}>
                            <h1 className={styles.greeting}>{getGreeting()}</h1>
                            <p className={styles.cta}>Tap the mic to start your session</p>
                        </div>
                    )}
                </div>

                <div className={styles.micButtonWrapper}>
                    {!isSessionActive ? (
                        <button className={styles.micButton} onClick={startSession}>
                            <MicIcon />
                        </button>
                    ) : (
                        <button className={`${styles.micButton} ${styles.active}`} onClick={stopSession}>
                            <StopIcon />
                        </button>
                    )}
                </div>
            </div>
        </div>
    );
};

const MicIcon = () => (
    <svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor" xmlns="http://www.w3.org/2000/svg">
        <path d="M12 14C13.6569 14 15 12.6569 15 11V5C15 3.34315 13.6569 2 12 2C10.3431 2 9 3.34315 9 5V11C9 12.6569 10.3431 14 12 14Z" />
        <path d="M18 11C18 14.3137 15.3137 17 12 17C8.68629 17 6 14.3137 6 11H4C4 15.4183 7.58172 19 12 19V22H12C16.4183 19 20 15.4183 20 11H18Z"/>
    </svg>
);

const StopIcon = () => (
    <svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor" xmlns="http://www.w3.org/2000/svg">
        <rect width="10" height="10" x="7" y="7" rx="1" />
    </svg>
);

export default ChatInterface; 