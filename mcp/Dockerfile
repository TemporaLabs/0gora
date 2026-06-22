FROM node:22-alpine
WORKDIR /app
COPY package.json ./
RUN npm install --omit=dev --no-fund --no-audit
COPY server ./server
EXPOSE 8091
CMD ["node", "server/http.js"]
