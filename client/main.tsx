import { createRoot } from "react-dom/client";
import { App } from "./App";

// Automatically reload if a dynamic import fails due to a new deployment
window.addEventListener("vite:preloadError", () => {
  window.location.reload();
});

window.addEventListener("error", (event) => {
  if (event?.message && event.message.includes("Failed to fetch dynamically imported module")) {
    window.location.reload();
  }
});

const rootElement = document.getElementById("root");

if (!rootElement) {
  throw new Error("Root element not found");
}

createRoot(rootElement).render(<App />);
