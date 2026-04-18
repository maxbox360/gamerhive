# frontend/Dockerfile
FROM node:20

WORKDIR /app

# Copy only package files first for caching
COPY package*.json ./

RUN npm install --legacy-peer-deps

# Copy the rest of the app
COPY . .

EXPOSE 3000
CMD ["npm", "run", "dev"]
