import React, { useState } from 'react';
import LoginForm from './LoginForm';
import RegisterForm from './RegisterForm';
import styles from '../../styles/Auth.module.css';

const AuthLayout = () => {
    const [isLogin, setIsLogin] = useState(true);

    const switchToRegister = () => setIsLogin(false);
    const switchToLogin = () => setIsLogin(true);

    return (
        <div className={styles.authPage}>
            <div className={styles.authContainer}>
                <div className={styles.authFormContainer}>
                    {isLogin ? (
                        <LoginForm switchToRegister={switchToRegister} />
                    ) : (
                        <RegisterForm switchToLogin={switchToLogin} />
                    )}
                </div>
                <div className={styles.authImageContainer}>
                    <img src="/images/person-learning.jpg" alt="Decorative background" className={styles.authBgImage} />
                    <div className={styles.imageOverlay}></div>
                    <div className={styles.imageContent}>
                        <h1 className={styles.imageTitle}>Welcome to Pistah</h1>
                        <p className={styles.imageSubtitle}>Your personal AI-powered speaking practice partner. Get ready to ace your IELTS test!</p>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default AuthLayout; 