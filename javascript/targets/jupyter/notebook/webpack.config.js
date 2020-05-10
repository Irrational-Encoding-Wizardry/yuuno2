const path = require('path');


const babel = (...additional) => [{
    loader: "babel-loader",
    options: {
        presets: ["@babel/preset-env"]
    },
    ...additional
}]
const style = (...additional) => [
    'style-loader', {
        loader: 'css-loader',
        options: {
            sourceMap: true
        }
    },
    ...additional
]

module.exports = {
    entry: './src/notebook.ts',
    module: {
        rules: [
            {
                test: /\.m?jsx?/,
                use: babel(),
                exclude: /node_modules/
            },
            {
                test: /.\tsx?$/,
                use: babel(),
                exclude: /node_modules/
            },
            {
                test: /\.css$/,
                use: style(),
                exclude: /node_modules/
            }
        ]
    },
    resolve: {
        extensions: ['.tsx', '.ts', '.js']
    },
    output: {
        filename: 'yuuno2notebook.js',
        path: path.resolve(__dirname, "lib"),
        
        libraryTarget: "amd",
        auxiliaryComment: "Yuuno2 Jupyter Notebook (JupyterLab)",

        externals: [
            '@jupyter-widgets/base'
        ]
    },
    devtool: "source-map"
};