const BundleTracker = require('webpack-bundle-tracker');
const CleanWebpackPlugin = require('clean-webpack-plugin');
const ExtractTextPlugin = require('extract-text-webpack-plugin');
const HtmlWebpackPlugin = require('html-webpack-plugin');
const path = require('path');
const webpack = require('webpack');

const outputPath = './public/bundles/';
const baseTemplatePath = './views/base.html';

const pathsToClean = [
    outputPath,
    baseTemplatePath
];

module.exports = {
  cache: true,

  context: __dirname,

  entry: {
    'main.style': './public/stylesheets/main.scss',
  },

  output: {
    path: path.resolve(outputPath),
    filename: '[name]-[hash].js',
    publicPath: '/static/bundles',
  },

  plugins: [
    new CleanWebpackPlugin(pathsToClean, { watch: true }),
    new BundleTracker({filename: './webpack-stats.json'}),
    new ExtractTextPlugin('[name]-[hash].css'),
    new HtmlWebpackPlugin({
      filename: path.resolve(baseTemplatePath),
      inject: 'body',
      template: 'views/base.tpl.html'
    }),
  ],

  module: {
    rules: [
      {
        test: /\.s?css$/,
        use: ExtractTextPlugin.extract({
          use: [
            {
              loader: 'css-loader',
              options: {
                minimize: true
              }
            },
            {
              loader: 'sass-loader'
            }
          ]
        })
      },
      {
        test: /\.woff2?$/,
        // Inline small woff files and output them below font
        loader: 'url-loader',
        query: {
          name: 'font/[name]-[hash].[ext]',
          limit: 5000,
          mimetype: 'application/font-woff'
        }
      },
      {
        test: /\.(ttf|eot|svg)$/,
        loader: 'file-loader',
        query: {
          name: 'font/[name]-[hash].[ext]'
        }
      }
    ]
  },
  resolve: {
    modules: ['./node_modules'],
    extensions: ['.css', '.scss']
  }
};
