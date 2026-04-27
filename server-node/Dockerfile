# Use Node 20 slim
FROM node:20-slim

# Install pnpm
RUN npm install -g pnpm

# Set working directory
WORKDIR /app

# Copy package.json and lock file
COPY server-node/package.json ./
COPY server-node/pnpm-lock.yaml ./

# Install dependencies
RUN pnpm install --prod

# Copy source code
COPY server-node/ .

# Expose port
EXPOSE 3001

# Run server
CMD ["node", "index.js"]
