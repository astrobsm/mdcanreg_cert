@echo off
echo ===================================
echo MDCAN BDM 2025 Certificate Platform
echo Asset Optimization Script
echo ===================================

echo.
echo Step 1: Installing optimization dependencies...
call npm install --save-dev compression-webpack-plugin terser-webpack-plugin image-minimizer-webpack-plugin

echo.
echo Step 2: Creating optimized webpack configuration...
echo const TerserPlugin = require('terser-webpack-plugin');> webpack.config.js
echo const CompressionPlugin = require('compression-webpack-plugin');>> webpack.config.js
echo const ImageMinimizerPlugin = require('image-minimizer-webpack-plugin');>> webpack.config.js
echo.>> webpack.config.js
echo module.exports = {>> webpack.config.js
echo   optimization: {>> webpack.config.js
echo     minimize: true,>> webpack.config.js
echo     minimizer: [>> webpack.config.js
echo       new TerserPlugin({>> webpack.config.js
echo         terserOptions: {>> webpack.config.js
echo           compress: {>> webpack.config.js
echo             drop_console: true,>> webpack.config.js
echo           },>> webpack.config.js
echo           output: {>> webpack.config.js
echo             comments: false,>> webpack.config.js
echo           },>> webpack.config.js
echo         },>> webpack.config.js
echo         extractComments: false,>> webpack.config.js
echo       }),>> webpack.config.js
echo     ],>> webpack.config.js
echo     splitChunks: {>> webpack.config.js
echo       chunks: 'all',>> webpack.config.js
echo       name: false,>> webpack.config.js
echo     },>> webpack.config.js
echo   },>> webpack.config.js
echo   plugins: [>> webpack.config.js
echo     new CompressionPlugin({>> webpack.config.js
echo       algorithm: 'gzip',>> webpack.config.js
echo       test: /\.(js|css|html|svg)$/,>> webpack.config.js
echo       threshold: 10240,>> webpack.config.js
echo       minRatio: 0.8,>> webpack.config.js
echo     }),>> webpack.config.js
echo     new ImageMinimizerPlugin({>> webpack.config.js
echo       minimizer: {>> webpack.config.js
echo         implementation: ImageMinimizerPlugin.imageminMinify,>> webpack.config.js
echo         options: {>> webpack.config.js
echo           plugins: [>> webpack.config.js
echo             ['imagemin-gifsicle', { interlaced: true }],>> webpack.config.js
echo             ['imagemin-mozjpeg', { quality: 80 }],>> webpack.config.js
echo             ['imagemin-pngquant', { quality: [0.6, 0.8] }],>> webpack.config.js
echo             ['imagemin-svgo', { plugins: [{ removeViewBox: false }] }],>> webpack.config.js
echo           ],>> webpack.config.js
echo         },>> webpack.config.js
echo       },>> webpack.config.js
echo     }),>> webpack.config.js
echo   ],>> webpack.config.js
echo };>> webpack.config.js

echo.
echo Step 3: Setting up environment for production...
echo GENERATE_SOURCEMAP=false> .env.production.local
echo REACT_APP_API_URL=https://mdcanbdm042-2025-mdcanreg-cert.ondigitalocean.app>> .env.production.local

echo.
echo Step 4: Building optimized production bundle...
call npm run build

echo.
echo Step 5: Optimizing images...
echo   - This may take a few moments...
cd public
for %%G in (*.png *.jpg *.jpeg) do (
    echo   - Optimizing %%G...
    magick convert %%G -strip -quality 85 %%G
)
cd ..

echo.
echo Step 6: Creating cache manifest...
echo {> build/cache-manifest.json
echo   "version": "1.0.0",>> build/cache-manifest.json
echo   "timestamp": "%DATE% %TIME%",>> build/cache-manifest.json
echo   "files": [>> build/cache-manifest.json
for /R build %%G in (*.*) do (
    echo     "%%~nxG",>> build/cache-manifest.json
)
echo   ]>> build/cache-manifest.json
echo }>> build/cache-manifest.json

echo.
echo Optimization complete!
echo Production build is ready in the 'build' folder.
echo.
echo ===================================
pause
