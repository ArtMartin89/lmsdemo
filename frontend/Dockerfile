FROM node:18-alpine AS build

WORKDIR /app

# Copy package files first for better caching
COPY package.json package-lock.json* ./

# Install dependencies with maximum optimizations
RUN npm install --prefer-offline --no-audit --legacy-peer-deps --progress=false --loglevel=error --maxsockets=1

# Copy source files
COPY . .

# Build the app
RUN npm run build

FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
