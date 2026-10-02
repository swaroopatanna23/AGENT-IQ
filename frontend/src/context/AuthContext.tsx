import React, { createContext, useContext, useState, useEffect } from "react";
import { User } from "../types";
import { authApi } from "../api/client";

interface AuthContextType {
  user: User | null;
  token: string | null;
  loading: boolean;
  login: (email: string, pass: string) => Promise<void>;
  register: (email: string, pass: string, name: string) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(localStorage.getItem("agentiq_token"));
  const [loading, setLoading] = useState<boolean>(true);

  useEffect(() => {
    const fetchUser = async () => {
      try {
        const res = await authApi.getMe();
        setUser(res.data);
      } catch (err) {
        localStorage.removeItem("agentiq_token");
        setToken(null);
        setUser(null);
      } finally {
        setLoading(false);
      }
    };
    fetchUser();
  }, [token]);

  const login = async (email: string, pass: string) => {
    const res = await authApi.login({ email, password: pass });
    const newToken = res.data.access_token;
    localStorage.setItem("agentiq_token", newToken);
    setToken(newToken);
    setUser(res.data.user);
  };

  const register = async (email: string, pass: string, name: string) => {
    const res = await authApi.register({ email, password: pass, full_name: name });
    const newToken = res.data.access_token;
    localStorage.setItem("agentiq_token", newToken);
    setToken(newToken);
    setUser(res.data.user);
  };

  const logout = () => {
    localStorage.removeItem("agentiq_token");
    setToken(null);
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, token, loading, login, register, logout }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) throw new Error("useAuth must be used within AuthProvider");
  return context;
};
