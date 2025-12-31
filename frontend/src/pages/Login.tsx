import React, { useState, useEffect, useRef } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../contexts/AuthContext";
import { Button } from "../components/ui/button";
import { API_BASE_URL } from "../config/api";

declare global {
  interface Window {
    google: any;
  }
}

const Login: React.FC = () => {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [isRegister, setIsRegister] = useState(false);
  const [name, setName] = useState("");
  const { login, register, loginWithGoogle } = useAuth();
  const navigate = useNavigate();
  const googleButtonRef = useRef<HTMLDivElement>(null);

  const handleGoogleSignIn = async (response: any) => {
    setError("");
    setLoading(true);

    try {
      await loginWithGoogle(response.credential);
      navigate("/");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Google sign-in failed");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    // Initialize Google Sign-In button
    const initGoogleSignIn = () => {
      const clientId = import.meta.env.VITE_GOOGLE_CLIENT_ID;
      if (!clientId) {
        console.warn(
          "Google Client ID not configured - Google Sign-In disabled"
        );
        return;
      }

      if (window.google && googleButtonRef.current) {
        window.google.accounts.id.initialize({
          client_id: clientId,
          callback: handleGoogleSignIn,
        });

        window.google.accounts.id.renderButton(googleButtonRef.current, {
          theme: "outline",
          size: "large",
          width: "100%",
          text: "signin_with",
        });
      }
    };

    // Wait for Google script to load
    if (window.google) {
      initGoogleSignIn();
    } else {
      const checkGoogle = setInterval(() => {
        if (window.google) {
          initGoogleSignIn();
          clearInterval(checkGoogle);
        }
      }, 100);

      return () => clearInterval(checkGoogle);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setLoading(true);

    try {
      if (isRegister) {
        await register(email, password, name);
      } else {
        await login(email, password);
      }
      navigate("/");
    } catch (err) {
      setError(err instanceof Error ? err.message : "An error occurred");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-[#1f0724]">
      <div className="max-w-md w-full space-y-8 p-8 bg-[#2a0f33] rounded-lg shadow-lg">
        <div>
          <h2 className="mt-6 text-center text-3xl font-extrabold text-white">
            {isRegister ? "Create an account" : "Sign in to your account"}
          </h2>
        </div>
        <form className="mt-8 space-y-6" onSubmit={handleSubmit}>
          {error && (
            <div className="bg-red-500/20 border border-red-500 text-red-200 px-4 py-3 rounded">
              {error}
            </div>
          )}
          <div className="space-y-4">
            {isRegister && (
              <div>
                <label
                  htmlFor="name"
                  className="block text-sm font-medium text-gray-300"
                >
                  Name
                </label>
                <input
                  id="name"
                  name="name"
                  type="text"
                  required
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  className="mt-1 appearance-none relative block w-full px-3 py-2 border border-gray-600 placeholder-gray-400 text-white bg-[#1f0724] rounded-md focus:outline-none focus:ring-purple-500 focus:border-purple-500"
                  placeholder="Your name"
                />
              </div>
            )}
            <div>
              <label
                htmlFor="email"
                className="block text-sm font-medium text-gray-300"
              >
                Email address
              </label>
              <input
                id="email"
                name="email"
                type="email"
                autoComplete="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="mt-1 appearance-none relative block w-full px-3 py-2 border border-gray-600 placeholder-gray-400 text-white bg-[#1f0724] rounded-md focus:outline-none focus:ring-purple-500 focus:border-purple-500"
                placeholder="Email address"
              />
            </div>
            <div>
              <label
                htmlFor="password"
                className="block text-sm font-medium text-gray-300"
              >
                Password
              </label>
              <input
                id="password"
                name="password"
                type="password"
                autoComplete="current-password"
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="mt-1 appearance-none relative block w-full px-3 py-2 border border-gray-600 placeholder-gray-400 text-white bg-[#1f0724] rounded-md focus:outline-none focus:ring-purple-500 focus:border-purple-500"
                placeholder="Password"
              />
            </div>
          </div>

          <div>
            <Button type="submit" disabled={loading} className="w-full">
              {loading ? "Loading..." : isRegister ? "Register" : "Sign in"}
            </Button>
          </div>

          <div className="relative">
            <div className="absolute inset-0 flex items-center">
              <div className="w-full border-t border-gray-600"></div>
            </div>
            <div className="relative flex justify-center text-sm">
              <span className="px-2 bg-[#2a0f33] text-gray-400">
                Or continue with
              </span>
            </div>
          </div>

          <div
            ref={googleButtonRef}
            className="w-full flex justify-center min-h-[40px]"
          >
            {!import.meta.env.VITE_GOOGLE_CLIENT_ID && (
              <p className="text-sm text-gray-500 text-center">
                Google Sign-In not configured. Add VITE_GOOGLE_CLIENT_ID to your
                .env file.
              </p>
            )}
          </div>

          <div className="text-center">
            <button
              type="button"
              onClick={() => {
                setIsRegister(!isRegister);
                setError("");
              }}
              className="text-sm text-purple-400 hover:text-purple-300"
            >
              {isRegister
                ? "Already have an account? Sign in"
                : "Don't have an account? Register"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default Login;
