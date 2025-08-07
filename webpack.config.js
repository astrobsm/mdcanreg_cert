const TerserPlugin = require('terser-webpack-plugin');
const CompressionPlugin = require('compression-webpack-plugin');
const ImageMinimizerPlugin = require('image-minimizer-webpack-plugin');

module.exports = {
  optimization: {
    minimize: true,
    minimizer: [
      new TerserPlugin({
        terserOptions: {
          compress: {
            drop_console: true,
            // Added settings to fix variable hoisting issues
            sequences: false,
            dead_code: true,
          },
          output: {
            comments: false,
          },
          // Fix variable access before initialization errors
          mangle: false,
        },
        extractComments: false,
      }),
    ],
    splitChunks: {
      chunks: 'all',
      name: false,
    },
  },
  plugins: [
    new CompressionPlugin({
      algorithm: 'gzip',
