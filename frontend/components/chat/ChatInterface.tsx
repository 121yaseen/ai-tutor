import React from 'react';
import { useAuth } from '@/hooks/useAuth';
import { useChatSession } from '@/hooks/useChatSession';

const ChatInterface = () => {
    const { user, logout } = useAuth();
    const { isSessionActive, conversation, startSession, stopSession } = useChatSession();

    // Greeting logic from original app.js
    const getGreeting = () => {
        const hour = new Date().getHours();
        if (hour < 5) return 'Good Night';
        if (hour < 12) return 'Good Morning';
        if (hour < 18) return 'Good Afternoon';
        return 'Good Evening';
    };

    return (
        <div className="container">
            <button onClick={logout} className="app-logout-button">Logout</button>
            <div className="voice-wave" id="voiceWave"></div>
            <div className="greeting">{getGreeting()}</div>
            <div className="cta">Tap to Start</div>
            
            {!isSessionActive ? (
                <button className="mic-btn" id="micBtn" onClick={startSession}>
                  <svg width="40" height="40" viewBox="0 0 40 40" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <circle cx="20" cy="20" r="18" stroke="#fff" strokeWidth="2" fill="none" />
                    <ellipse cx="20" cy="18" rx="7" ry="10" fill="#fff" opacity="0.12" />
                    <rect x="15" y="12" width="10" height="16" rx="5" fill="#fff" stroke="#fff" strokeWidth="2"/>
                    <rect x="18" y="28" width="4" height="6" rx="2" fill="#fff" />
                    <line x1="20" y1="34" x2="20" y2="38" stroke="#fff" strokeWidth="2" strokeLinecap="round"/>
                  </svg>
                </button>
            ) : (
                <button className="stop-btn" id="stopBtn" onClick={stopSession} style={{ marginBottom: '32px' }}>
                  <svg width="40" height="40" viewBox="0 0 40 40" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <circle cx="20" cy="20" r="18" stroke="#fff" strokeWidth="2" fill="none" />
                    <rect x="14" y="14" width="12" height="12" rx="3" fill="#fff" opacity="0.18" />
                    <rect x="16" y="16" width="8" height="8" rx="2" fill="#fff" opacity="0.85" />
                  </svg>
                </button>
            )}
            
            <div className="conversation" id="conversation">
                {conversation.map((message) => (
                    <p key={message.id}>
                        {message.content}
                    </p>
                ))}
            </div>
        </div>
    );
};

export default ChatInterface; 