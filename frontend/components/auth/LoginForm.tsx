import React, { useState } from 'react';
import { useAuth } from '@/hooks/useAuth';
import { useRouter } from 'next/router';

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
        <form id="login-form" className="auth-form" onSubmit={handleSubmit}>
            <h2 className="auth-title">Welcome back to Pistah!</h2>
            <p className="auth-subtitle">Build your design system effortlessly with our powerful component library.</p>
            
            <label htmlFor="login-username">Email</label>
            <div className="input-group modern-input">
                <input 
                    type="text" 
                    id="login-username" 
                    placeholder="alex.jordan@gmail.com" 
                    required 
                    autoComplete="username"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                />
            </div>
            
            <label htmlFor="login-password">Password</label>
            <div className="input-group modern-input focused">
                <input 
                    type="password" 
                    id="login-password" 
                    placeholder="••••••••" 
                    required 
                    autoComplete="current-password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                />
            </div>

            <div className="form-options">
                <a href="#" className="forgot-password">Forgot password?</a>
                <div className="remember-me">
                    <span>Remember sign in details</span>
                    <label className="switch">
                        <input type="checkbox" />
                        <span className="slider round"></span>
                    </label>
                </div>
            </div>
            
            <button type="submit" className="modern-btn primary-btn login-action-btn">Log in</button>
            {error && <span id="login-error" className="auth-error">{error}</span>}

            <div className="form-divider">OR</div>

            <button type="button" className="modern-btn google-btn">
                <img src="https://upload.wikimedia.org/wikipedia/commons/thumb/c/c1/Google_%22G%22_logo.svg/768px-Google_%22G%22_logo.svg.png" alt="Google logo" className="google-icon"/> 
                Continue with Google
            </button>

            <p className="auth-toggle-text">
                Don't have an account? <button type="button" onClick={switchToRegister} className="link-btn">Sign up</button>
            </p>
        </form>
    );
};

export default LoginForm; 