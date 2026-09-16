import { defineConfig } from "vite";
import react from "@vitejs/plugin-react-swc";
import path from "path";
import { fileURLToPath } from "node:url";

const projectRoot = fileURLToPath(new URL(".", import.meta.url));

export default defineConfig(({ mode }) => ({
  root: path.resolve(projectRoot, "client"),
  envDir: "../",

  server: {
    host: "0.0.0.0",
    port: 8080,
    proxy: {
      "/api": {
        target: "http://127.0.0.1:8001",
        changeOrigin: true,
        secure: false,
      },
      "/uploads": {
        target: "http://127.0.0.1:8001",
        changeOrigin: true,
        secure: false,
      },
    },
    fs: {
      allow: [projectRoot],
      deny: [".env", ".env.*", "*.{crt,pem}", "**/.git/**", "server/**"],
    },
  },
  build: {
    outDir: path.resolve(projectRoot, "dist/spa"),
    emptyOutDir: true,
  },
  plugins: [react()],
  resolve: {
    alias: {
      "@": path.resolve(projectRoot, "./client"),
      "@shared": path.resolve(projectRoot, "./shared"),
    },
  },
}));
