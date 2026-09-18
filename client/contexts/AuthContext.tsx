import React, { createContext, useContext, useState, useEffect } from "react";
import { toast } from "sonner";
import { io } from "socket.io-client";

const SOCKET_SERVER_URL = import.meta.env.PROD 
  ? window.location.origin 
  : "http://localhost:3001";

interface User {
  id: number;
  email: string;
  name: string;
  role: 'teacher' | 'student' | 'unassigned';
  studentId?: string;
  teacherId?: string;
  avatarUrl?: string;
  is_verified?: number;
}

interface AuthContextType {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (token: string, userData: User) => void;
  logout: () => void;
  loginWithFirebase: (firebaseToken: string) => Promise<void>;
  updateUser: (userData: Partial<User>) => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(localStorage.getItem("token"));
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    let disposed = false;
    let currentSocket: ReturnType<typeof io> | undefined;

    const connectSocket = async () => {
      if (!user || !token) return;
      try {
        const tokenResponse = await fetch("/api/auth/socket-token", {
          method: "POST",
          headers: { Authorization: `Bearer ${token}` },
        });
        if (!tokenResponse.ok) throw new Error("Unable to create socket token");
        const { socket_token: socketToken } = await tokenResponse.json();
        if (disposed) return;

        currentSocket = io(SOCKET_SERVER_URL, {
          transports: ['websocket'],
          reconnectionAttempts: 3,
          auth: { token: socketToken },
        });
        currentSocket.on("connect", () => {
          console.log("Connected to Real-time Notification Server");
        });

        currentSocket.on("connect_error", (err) => {
          console.warn("Socket connection error (Node server might be down):", err.message);
        });

        currentSocket.on("new_notification", (data) => {
          console.log("Received notification:", data);
          window.dispatchEvent(new CustomEvent("evaly:notification", { detail: data }));
          toast(data.message || "มีการแจ้งเตือนใหม่", {
            description: "กดเพื่อดูรายละเอียด",
            action: data.data?.link ? {
              label: "ดูห้องเรียน",
              onClick: () => window.location.href = data.data.link
            } : undefined,
            duration: 10000,
          });
        });

      } catch (e) {
        console.error("Socket initialization failed:", e);
      }
    };

    connectSocket();
    return () => {
      disposed = true;
      currentSocket?.disconnect();
    };
  }, [user?.id, token]);

  useEffect(() => {
    const fetchUser = async () => {
      if (!token) {
        setIsLoading(false);
        return;
      }

      try {
        const response = await fetch("/api/auth/me", {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        });

        if (response.ok) {
          const userData = await response.json();
          setUser(userData);
        } else {
          // Token expired or invalid
          logout();
        }
      } catch (error) {
        console.error("Fetch user error:", error);
      } finally {
        setIsLoading(false);
      }
    };

    fetchUser();
  }, [token]);

  const login = (newToken: string, userData: User) => {
    localStorage.setItem("token", newToken);
    setToken(newToken);
    setUser(userData);
    toast.success("เข้าสู่ระบบสำเร็จ");
  };

  const logout = async () => {
    try {
      await fetch("/api/auth/logout", { method: "POST" });
    } catch (e) {
      console.error("Logout cookie clear error:", e);
    }
    localStorage.removeItem("token");
    setToken(null);
    setUser(null);
    toast.info("ออกจากระบบแล้ว");
  };

  const updateUser = (userData: Partial<User>) => {
    if (user) {
      setUser({ ...user, ...userData });
    }
  };

  const loginWithFirebase = async (firebaseToken: string) => {
    try {
      const response = await fetch("/api/auth/firebase-login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ firebase_token: firebaseToken }),
      });

      const data = await response.json();

      if (response.ok) {
        login(data.access_token, data.user);
      } else {
        throw new Error(data.detail || "Firebase login failed");
      }
    } catch (error) {
      console.error("Firebase login error:", error);
      throw error;
    }
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        token,
        isAuthenticated: !!user,
        isLoading,
        login,
        logout,
        loginWithFirebase,
        updateUser,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
};
