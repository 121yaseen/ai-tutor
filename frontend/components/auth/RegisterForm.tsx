import React, { useState } from 'react';
import { useAuth } from '@/hooks/useAuth';
import styles from '../../styles/Auth.module.css';

interface RegisterFormProps {
    switchToLogin: () => void;
}

const RegisterForm: React.FC<RegisterFormProps> = ({ switchToLogin }) => {
    const { register } = useAuth();
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [confirmPassword, setConfirmPassword] = useState('');
    const [error, setError] = useState('');
    const [success, setSuccess] = useState('');

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setError('');
        setSuccess('');

        if (password !== confirmPassword) {
            setError('Passwords do not match.');
            return;
        }

        const isSuccess = await register(email, password);

        if (isSuccess) {
            setSuccess('Registration successful! Please log in.');
            setTimeout(() => {
                switchToLogin();
            }, 2000);
        } else {
            setError('Registration failed. Please try again.');
        }
    };

    return (
        <div className={styles.form}>
            <h2 className={styles.title}>Create Account</h2>
            <p className={styles.subtitle}>Get started with your personal AI tutor.</p>
            
            <form onSubmit={handleSubmit}>
                <div className={styles.inputGroup}>
                    <label htmlFor="register-email">Email</label>
                    <input 
                        type="email" 
                        id="register-email" 
                        placeholder="you@example.com" 
                        required 
                        autoComplete="email"
                        value={email}
                        onChange={(e) => setEmail(e.target.value)}
                        className={styles.input}
                    />
                </div>
                
                <div className={styles.inputGroup}>
                    <label htmlFor="register-password">Password</label>
                    <input 
                        type="password" 
                        id="register-password" 
                        placeholder="••••••••" 
                        required 
                        autoComplete="new-password"
                        value={password}
                        onChange={(e) => setPassword(e.target.value)}
                        className={styles.input}
                    />
                </div>

                <div className={styles.inputGroup}>
                    <label htmlFor="confirm-password">Confirm Password</label>
                    <input 
                        type="password" 
                        id="confirm-password" 
                        placeholder="••••••••" 
                        required 
                        autoComplete="new-password"
                        value={confirmPassword}
                        onChange={(e) => setConfirmPassword(e.target.value)}
                        className={styles.input}
                    />
                </div>
                
                <button type="submit" className={styles.submitButton}>Sign Up</button>
                {error && <p className={styles.error}>{error}</p>}
                {success && <p className={styles.success}>{success}</p>}
            </form>

            <p className={styles.toggleText}>
                Already have an account? <button onClick={switchToLogin} className={styles.toggleButton}>Log in</button>
            </p>
        </div>
    );
};

export default RegisterForm; 