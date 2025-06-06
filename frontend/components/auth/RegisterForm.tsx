import React, { useState } from 'react';
import { useAuth } from '@/hooks/useAuth';

interface RegisterFormProps {
    switchToLogin: () => void;
}

const RegisterForm: React.FC<RegisterFormProps> = ({ switchToLogin }) => {
    const { register } = useAuth();
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState('');

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setError('');
        const success = await register(email, password);
        if (success) {
            // Automatically switch to login form after successful registration
            switchToLogin();
        } else {
            setError('Registration failed. The email might already be in use.');
        }
    };

    return (
        <form id="register-form" className="auth-form" onSubmit={handleSubmit}>
            <h2 className="auth-title">Create Your Pistah Account</h2>
            <p className="auth-subtitle">Join us and start building amazing things.</p>

            <label htmlFor="register-email">Email</label>
            <div className="input-group modern-input">
                <input 
                    type="email" 
                    id="register-email" 
                    placeholder="your.email@example.com" 
                    required 
                    autoComplete="email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                />
            </div>

            <label htmlFor="register-password">Password</label>
            <div className="input-group modern-input">
                <input 
                    type="password" 
                    id="register-password" 
                    placeholder="Create a strong password" 
                    required 
                    autoComplete="new-password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                />
            </div>
            
            <button type="submit" className="modern-btn primary-btn login-action-btn">Register</button>
            {error && <span id="register-error" className="auth-error">{error}</span>}

            <p className="auth-toggle-text">
                Already have an account? <button type="button" onClick={switchToLogin} className="link-btn">Log In</button>
            </p>
        </form>
    );
};

export default RegisterForm; 