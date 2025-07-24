module.exports = {
  devServer: {
    proxy: {
      '/api': {
        target: 'http://localhost:12000',
        changeOrigin: true
      }
    },
    allowedHosts: "all"
  }
}