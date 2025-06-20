import { Navigate} from "react-router-dom";
import { ReactNode } from "react";
import { useAuth } from "../context/AuthContext";

interface AdminRouteProps {
  children: ReactNode;
}

export function AdminRoute({ children }: AdminRouteProps) {
  const { userData } = useAuth();

  if (userData === null) {
    return null;
  }

  if (!userData.is_admin) {
    return <Navigate to="/" replace />;
  }

  return <>{children}</>;
}

