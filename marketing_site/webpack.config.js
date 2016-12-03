var path = require('path'),
    webpack = require('webpack'),
    BundleTracker = require('webpack-bundle-tracker'),
    ExtractTextPlugin = require('extract-text-webpack-plugin'),
    PurifyPlugin = require('purifycss-webpack-plugin');

module.exports = {
    context: __dirname,

    entry: {
        base: './static/js/base.js',
        'base.style': './static/sass/base.scss'
    },

    output: {
        path: path.resolve('./static/bundles/'),
        filename: '[name]-[hash].js'
    },

    plugins: [
        new BundleTracker({filename: './webpack-stats.json'}),
        new ExtractTextPlugin('[name]-[hash].css'),
        new webpack.ProvidePlugin({
            $: 'jquery',
            jQuery: 'jquery'
        }),
        // NOTE: The purify plugin finds, and removes, unused CSS. This process can be slow (~3x increase in
        // compilation times), but results in significantly smaller CSS files. Consider disabling this plugin—-comment
        // out the instantiation below-—during development; but, remember to review your work with it enabled,
        // in case it is too aggressive and removes needed styles.
        // new PurifyPlugin({
        //     basePath: __dirname,
        //     paths: ['**/*.html'],
        //     resolveExtensions: ['.html'],
        //     purifyOptions: {
        //         minify: true,
        //         info: true,
        //         rejected: true
        //     }
        // })
    ],

    module: {
        loaders: [
            {
                test: /\.js$/,
                exclude: /(node_modules)/,
                loader: 'babel-loader',
                query: {
                    cacheDirectory: true,
                    presets: ['latest']
                }
            },
            {
                test: /\.s?css$/,
                loader: ExtractTextPlugin.extract({
                    fallbackLoader: 'style-loader',
                    loader: [
                        {
                            loader: 'css-loader',
                            options: {
                                minimize: true
                            }
                        },
                        {
                            loader: 'sass-loader',
                            options: {
                                includePaths: [path.resolve('../node_modules'), path.resolve('./static/sass/')]
                            }
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
            },
        ]
    },
    resolve: {
        modules: ['../node_modules'],
        extensions: ['.css', '.js', '.scss']
    }
};
