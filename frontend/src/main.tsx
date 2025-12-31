import React from "react";
import { createRoot } from "react-dom/client";
import { BrowserRouter } from "react-router-dom";
import "./styles/style.css";
import App from "./App";
import ErrorBoundary from "./components/ErrorBoundary";

const rootElement = document.getElementById("root");
if (!rootElement) {
  throw new Error("Root element not found");
}

createRoot(rootElement).render(
  <React.StrictMode>
    <ErrorBoundary>
      <BrowserRouter>
        <App />
      </BrowserRouter>
    </ErrorBoundary>
  </React.StrictMode>
);
