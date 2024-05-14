/* eslint-disable no-unused-vars */
const path = require('path')
const webpack = require('webpack')
const BundleTracker = require('webpack-bundle-tracker')
const CopyPlugin = require('copy-webpack-plugin')
const MiniCssExtractPlugin = require('mini-css-extract-plugin')
const Dotenv = require('dotenv-webpack')
const WebSocket = require('ws')
const StylelintPlugin = require('stylelint-webpack-plugin')

require('dotenv').config({ path: '../../.env.local' })

const devMode = process.env.NODE_ENV !== 'production'
const git_sha = process.env.GITHUB_SHA
class CustomPlugin {
  constructor(name, port = 9000, stage = 'afterEmit') {
    this.name = name
    this.stage = stage
    try {
      this.server = new WebSocket.Server({
        port: port,
      })
      let sockets = []
      this.server.on('connection', function (socket) {
        sockets.push(socket)

        // When you receive a message, send that message to every socket.
        socket.on('message', function (msg) {
          sockets.forEach((s) => s.send(msg))
        })

        // When a socket closes, or disconnects, remove it from the array.
        socket.on('close', function () {
          sockets = sockets.filter((s) => s !== socket)
        })
      })
    } catch (error) {
      console.error(error)
    }
  }

  apply(compiler) {
    if (this.server.clients) {
      compiler.hooks[this.stage].tap(this.name, () => {
        try {
          this.server.clients.forEach(function each(client) {
            if (client.readyState === WebSocket.OPEN) {
              client.send('reload')
            }
          })
        } catch (error) {
          console.error(error)
        }
      })
    }
  }
}

let config = {
  context: __dirname,
  mode: 'development',
  entry: { app: './assets/app.js' },
  output: {
    path: path.resolve('./public/build/'),
    filename: '[name]-[hash].js',
    publicPath: '/static/',
    clean: true,
  },
  devServer: {
    static: {
      directory: path.join(__dirname, 'public'),
    },
    compress: true,
    port: 8008,
    allowedHosts: ['frontend', 'localhost', 'host.docker.internal'],
    headers: {
      'Access-Control-Allow-Origin': '*',
      'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, PATCH, OPTIONS',
      'Access-Control-Allow-Headers': 'X-Requested-With, content-type, Authorization',
    },
  },
  module: {
    rules: [
      {
        test: /\.(sa|sc|c)ss$/,
        use: [MiniCssExtractPlugin.loader, 'css-loader', 'postcss-loader', 'sass-loader'],
      },
      {
        test: /\.m?js$/,
        exclude: /(node_modules|bower_components)/,
        use: {
          loader: 'babel-loader',
          options: {
            presets: ['@babel/preset-env'],
          },
        },
      },
    ],
  },
}

module.exports = (env, argv) => {
  if (argv.nodeEnv === 'development') {
    config.output.path = path.resolve('./public/build/')
    config.devtool = 'source-map'
    config.output.filename = '[name].js'
  }

  config.plugins = [
    new MiniCssExtractPlugin({ filename: '[name]-[hash].css' }),
    new StylelintPlugin({
      context: path.resolve(__dirname, 'scss'),
      customSyntax: 'postcss-scss',
    }),
    new CopyPlugin({
      patterns: [
        {
          from: './assets/images/*.*',
          globOptions: {
            patterns: '*.+(png|jpg|jpeg|svg|ico)',
          },
          to: 'images/[name][ext]',
        },
        {
          from: './assets/icons/*.svg',
          to: 'icons/[name][ext]',
        },
        {
          from: './assets/script/*.js',
          to: 'script/[name][ext]',
        },
        {
          from: './assets/manifest.json',
          to: '[name][ext]',
        },
      ],
    }),
    new Dotenv({ path: '../../.env.local' }),
    new BundleTracker({ filename: './public/build/webpack-stats.json' }),
  ]
  if (argv.nodeEnv === 'development') {
    config.plugins.push(new CustomPlugin('Reloader', process.env.DEV_SOCKET_PORT, 'done'))
  }

  return config
}
