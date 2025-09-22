const { defineConfig } = require('@vue/cli-service')
module.exports = {
  devServer: {
    port: 8080,          // 前端开发服务器端口（可自定义，避免冲突）
    host: '0.0.0.0',     // 允许外部设备访问（如本地电脑访问容器内前端）
    allowedHosts: 'all', // 解决“无效主机”错误（开发环境安全）
    proxy: {
      // 匹配所有以 /api 开头的请求（前端调用 API 时用 /api/xxx）
      '/api': {
        target: 'http://localhost:8001', // 后端 API 地址（后端运行的地址+端口）
        changeOrigin: true,              // 开启跨域（关键：伪装请求来源，避免跨域拦截）
        pathRewrite: {
          // '^/api': '' // 可选：若后端 API 没有 /api 前缀，需去掉（例：前端 /api/user → 后端 /user）
        }
      }
    }
  }
};