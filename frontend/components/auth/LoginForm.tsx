import React, { useState } from 'react';
import { useAuth } from '@/hooks/useAuth';
import { useRouter } from 'next/router';
import styles from '../../styles/Auth.module.css';

interface LoginFormProps {
    switchToRegister: () => void;
}

const LoginForm: React.FC<LoginFormProps> = ({ switchToRegister }) => {
    const { login } = useAuth();
    const router = useRouter();
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState('');

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setError('');
        const success = await login(email, password);
        if (success) {
            router.push('/ai-tutor');
        } else {
            setError('Invalid credentials. Please try again.');
        }
    };

    return (
        <div className={styles.form}>
            <h2 className={styles.title}>Welcome Back!</h2>
            <p className={styles.subtitle}>Please sign in to continue.</p>
            
            <form onSubmit={handleSubmit}>
                <div className={styles.inputGroup}>
                    <label htmlFor="login-email">Email</label>
                    <input 
                        type="email" 
                        id="login-email" 
                        placeholder="you@example.com" 
                        required 
                        autoComplete="email"
                        value={email}
                        onChange={(e) => setEmail(e.target.value)}
                        className={styles.input}
                    />
                </div>
                
                <div className={styles.inputGroup}>
                    <label htmlFor="login-password">Password</label>
                    <input 
                        type="password" 
                        id="login-password" 
                        placeholder="••••••••" 
                        required 
                        autoComplete="current-password"
                        value={password}
                        onChange={(e) => setPassword(e.target.value)}
                        className={styles.input}
                    />
                </div>

                <div className={styles.formOptions}>
                    <a href="#" className={styles.forgotPassword}>Forgot password?</a>
                </div>
                
                <button type="submit" className={styles.submitButton}>Log In</button>
                {error && <p className={styles.error}>{error}</p>}
            </form>

            <p className={styles.toggleText}>
                Don't have an account? <button onClick={switchToRegister} className={styles.toggleButton}>Sign up</button>
            </p>
        </div>
    );
};

export default LoginForm; 