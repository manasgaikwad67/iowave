FROM node:20-alpine

# Set working directory
WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm ci

# Copy application code
COPY . .

# Build for production
RUN npm run build

# Install serve for production
RUN npm install -g serve

# Expose port
EXPOSE 5173

# Start preview server (for development)
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]