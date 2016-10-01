var BundleTracker = require('webpack-bundle-tracker'),
    ExtractTextPlugin = require('extract-text-webpack-plugin'),
    path = require('path'),
    webpack = require('webpack'),
    loaders = [
        {
            loader: 'css-loader',
            options: {
                minimize: true
            }
        },
        {
            loader: 'sass-loader',
            options: {
                includePaths: [path.resolve('./sass/')]
            }
        }
    ],
    context = path.join(__dirname, 'marketing_site/static');

module.exports = {
    context: context,

    entry: {
        base: './js/base.js',
        'base.style': './sass/base.scss'
    },

    output: {
        path: path.join(context, './bundles/'),
        filename: '[name]-[hash].js'
    },

    plugins: [
        new BundleTracker({filename: './webpack-stats.json'}),
        new webpack.ProvidePlugin({
            $: 'jquery',
            jQuery: 'jquery',
            'window.jQuery': 'jquery'
        }),
        new ExtractTextPlugin('[name]-[hash].css')
    ],

    module: {
        rules: [
            {
                test: /\.s?css$/,
                use: ExtractTextPlugin.extract({
                    fallback: 'style-loader',
                    use: loaders
                })
            },
            {
                test: /\.woff2?$/,
                // Inline small woff files and output them below font
                use: [{
                    loader: 'url-loader',
                    options: {
                        name: 'font/[name]-[hash].[ext]',
                        limit: 5000,
                        mimetype: 'application/font-woff'
                    }
                }]
            },
            {
                test: /\.(ttf|eot|svg)$/,
                use: [{
                    loader: 'file-loader',
                    options: {
                        name: 'font/[name]-[hash].[ext]'
                    }
                }]
            }
        ]
    },
    resolve: {
        modules: ['node_modules'],
        extensions: ['.css', '.js', '.scss']
    }
};
