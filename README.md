# edx-marketing-site-frontend

## Development

Install all dependencies:

    $ npm install

Run Webpack in watch mode:

    $ npm run watch

Run the webserver:

    $ npm start

## Deployment

Static assets are compiled by Webpack and pushed to S3.

    $ npm run build

Application code is deployed to AWS API Gateway + Lambda (server code) using [ClaudiaJS](https://claudiajs.com/). 

    $ npm run deploy
