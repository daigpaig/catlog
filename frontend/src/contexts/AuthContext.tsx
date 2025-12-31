import React, {
  createContext,
  useContext,
  useState,
  useEffect,
  ReactNode,
} from "react";
import { apiService } from "../services/api";
import type { UserResponse } from "../types/api";

interface AuthContextType {
  user: UserResponse | null;
  loading: boolean;
  isAuthenticated: boolean;
  login: (email: string, password: string) => Promise<void>;
  loginWithGoogle: (googleToken: string) => Promise<void>;
  logout: () => void;
  register: (email: string, password: string, name: string) => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
};

interface AuthProviderProps {
  children: ReactNode;
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [user, setUser] = useState<UserResponse | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let isMounted = true;

    // Check if user is already authenticated on mount
    const checkAuth = async () => {
      try {
        const token = localStorage.getItem("access_token");
        if (token) {
          try {
            const userData = await apiService.getCurrentUser();
            if (isMounted) {
              setUser(userData);
            }
          } catch (error) {
            // Token is invalid, clear it
            console.log("Auth check failed, clearing tokens:", error);
            apiService.clearAuthTokens();
            if (isMounted) {
              setUser(null);
            }
          }
        } else {
          // No token, user is not authenticated
          if (isMounted) {
            setUser(null);
          }
        }
      } catch (error) {
        console.error("Error checking auth:", error);
        if (isMounted) {
          setUser(null);
        }
      } finally {
        if (isMounted) {
          setLoading(false);
        }
      }
    };

    // Add a timeout to prevent infinite loading
    const timeout = setTimeout(() => {
      if (isMounted) {
        console.warn("Auth check timed out, setting loading to false");
        setLoading(false);
      }
    }, 5000);

    checkAuth();

    return () => {
      isMounted = false;
      clearTimeout(timeout);
    };
  }, []);

  const login = async (email: string, password: string) => {
    await apiService.login(email, password);
    const userData = await apiService.getCurrentUser();
    setUser(userData);
  };

  const loginWithGoogle = async (googleToken: string) => {
    await apiService.loginWithGoogle(googleToken);
    const userData = await apiService.getCurrentUser();
    setUser(userData);
  };

  const logout = () => {
    apiService.clearAuthTokens();
    setUser(null);
  };

  const register = async (email: string, password: string, name: string) => {
    await apiService.register(email, password, name);
    const userData = await apiService.getCurrentUser();
    setUser(userData);
  };

  const value: AuthContextType = {
    user,
    loading,
    isAuthenticated: !!user,
    login,
    loginWithGoogle,
    logout,
    register,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};
