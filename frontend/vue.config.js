module.exports = {
  devServer: {
    headers: {
      "Access-Control-Allow-Origin": "*",
      "Access-Control-Allow-Credentials": "true",
      "Access-Control-Allow-Methods": "GET,HEAD,OPTIONS,POST,PUT",
      "Access-Control-Allow-Headers":
        "Origin, X-Requested-With, Content-Type, Accept, Authorization, X-Auth-Token",
    },
    proxy: {
      "/api": {
        target: "http://10.133.6.45:8000/",
        changeOrigin: true,
        pathRewrite: {
          "^/api": "/api",
        },
      },
    },
    // proxy: "http://10.133.6.45:8000/",
  },
};
