FROM node:22-alpine
WORKDIR /app
COPY package.json ./
RUN npm install --omit=dev --no-fund --no-audit
COPY src ./src
EXPOSE 8091
CMD ["node", "src/http.js"]
