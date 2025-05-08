import { createRoot } from "react-dom/client";
import App from "./App";
import "./index.css";

// Initialize feather icons if available
document.addEventListener("DOMContentLoaded", () => {
  if (typeof feather !== 'undefined' && feather.replace) {
    feather.replace();
  }
});

createRoot(document.getElementById("root")!).render(<App />);
