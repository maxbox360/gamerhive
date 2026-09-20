"use client";

import { createContext, ReactNode, useCallback, useContext, useEffect, useState } from "react";
import { getCurrentUser, User } from "@/utils/auth";

type AuthContextValue = {
  user: User | null;
  isLoading: boolean;
  error: Error | null;
  refreshUser: () => Promise<void>;
};

const AuthContext = createContext<AuthContextValue | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  const refreshUser = useCallback(async () => {
    setIsLoading(true);
    setError(null);

    try {
      setUser(await getCurrentUser());
    } catch (err) {
      setUser(null);
      setError(err instanceof Error ? err : new Error("Could not determine the current session."));
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    void refreshUser();
  }, [refreshUser]);

  return (
    <AuthContext.Provider value={{ user, isLoading, error, refreshUser }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);

  if (!context) {
    throw new Error("useAuth must be used within an AuthProvider.");
  }

  return context;
}
