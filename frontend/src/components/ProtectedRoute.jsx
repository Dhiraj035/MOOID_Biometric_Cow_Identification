import { useEffect, useState } from "react";
import { Navigate } from "react-router-dom";

import {
  getCurrentUser,
  getToken,
} from "../services/api";

function ProtectedRoute({ children }) {

  const [checking, setChecking] = useState(true);
  const [authenticated, setAuthenticated] = useState(false);

  useEffect(() => {

    async function checkAuthentication() {

      const token = getToken();

      if (!token) {
        setAuthenticated(false);
        setChecking(false);
        return;
      }

      try {

        await getCurrentUser();

        setAuthenticated(true);

      } catch (error) {

        setAuthenticated(false);

      } finally {

        setChecking(false);

      }
    }

    checkAuthentication();

  }, []);

  // While checking JWT
  if (checking) {

    return (
      <div className="auth-loading">
        Checking authentication...
      </div>
    );

  }

  // User is not authenticated
  if (!authenticated) {

    return (
      <Navigate
        to="/login"
        replace
      />
    );

  }

  // User is authenticated
  return children;
}

export default ProtectedRoute;