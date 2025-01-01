# 构建阶段
FROM node:16 AS build-stage

# 设置工作目录
WORKDIR /app

# 复制 package.json 和 package-lock.json
COPY package*.json ./

# 安装 cnpm
RUN npm install -g cnpm --registry=https://registry.npmmirror.com

# 使用 cnpm 安装依赖
RUN cnpm install

# 复制所有源代码
COPY . .

# 添加调试信息
RUN pwd && ls -la

# 使用 vite 构建
RUN npm run build

# 生产阶段
FROM nginx:alpine AS production-stage

# 从构建阶段复制 dist 文件
COPY --from=build-stage /app/dist /usr/share/nginx/html

# 复制 nginx 配置
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"] 