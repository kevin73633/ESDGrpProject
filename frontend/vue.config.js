const { defineConfig } = require('@vue/cli-service')
module.exports = defineConfig({
  transpileDependencies: true,
  lintOnSave: false // Temporarily disable ESLint in Webpack to isolate the issue
})
