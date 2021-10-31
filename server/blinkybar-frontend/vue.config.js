const path = require("path");

module.exports = {
    outputDir: path.resolve(__dirname, "../static"),
    devServer: {
        proxy: {
            '/.*': {
                target: 'http://localhost:8080'
            },
        }
    }
}