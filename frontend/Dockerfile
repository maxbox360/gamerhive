# frontend/Dockerfile
FROM node:20

WORKDIR /app

# Copy only package files first for caching
COPY package*.json ./

# Use legacy-peer-deps to avoid React/EUI conflicts
RUN npm uninstall @elastic/eui @elastic/datemath --legacy-peer-deps || true \
    && npm uninstall react react-dom @types/react @types/react-dom --legacy-peer-deps || true \
    && npm install react@18 react-dom@18 --legacy-peer-deps \
    && npm install --save-dev @types/react@18 @types/react-dom@18 --legacy-peer-deps \
    && npm install @elastic/eui@111 @elastic/datemath --legacy-peer-deps \
    && npm install --legacy-peer-deps

# Copy the rest of the app
COPY . .

EXPOSE 3000
CMD ["npm", "run", "dev"]
