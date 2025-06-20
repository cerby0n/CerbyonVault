import { Navigate} from "react-router-dom";
import { JSX, ReactNode, useContext } from "react";
import { AuthContext } from "../context/AuthContext";

interface Props { children: ReactNode }

export const PrivateRoute = ({children}:Props): JSX.Element =>{
    const ctx = useContext(AuthContext);
    if (!ctx) throw new Error("⛔ Must be inside <AuthProvider>");

   return ctx.user
    ? <>{children}</>
    : <Navigate to="/login" replace/>;
}

