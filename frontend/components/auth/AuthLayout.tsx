import { useState } from 'react';
import LoginForm from './LoginForm';
import RegisterForm from './RegisterForm';

const AuthLayout = () => {
    const [isLogin, setIsLogin] = useState(true);

    const switchToRegister = () => setIsLogin(false);
    const switchToLogin = () => setIsLogin(true);

    return (
        <div className="login-page-wrapper">
            <div className="login-info-column">
                <div className="login-logo">
                    <img src="/images/pistah.svg" alt="Pistah Logo" />
                </div>
                <div className="login-testimonial-image">
                    <img src="/images/person-learning.jpg" alt="Person learning with headphones" />
                </div>
                <div className="login-testimonial-text">
                    <blockquote>
                        "Simply all the tools that my team and I need."
                    </blockquote>
                    <p className="testimonial-author">Karen Yue</p>
                    <p className="testimonial-role">Director of Digital Marketing Technology</p>
                </div>
            </div>
            <div className="login-form-column">
                {isLogin ? (
                    <LoginForm switchToRegister={switchToRegister} />
                ) : (
                    <RegisterForm switchToLogin={switchToLogin} />
                )}
            </div>
        </div>
    );
};

export default AuthLayout; 