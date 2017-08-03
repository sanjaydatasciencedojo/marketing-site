const express = require('express');
const favicon = require('serve-favicon');
const logger = require('morgan');
const nunjucks = require('nunjucks');
const path = require('path');

const index = require('./routes/index');

const app = express();
const env = app.get('env');
const isDev = env === 'development';
const config = require('./config/config.json')[env];
const publicPath = path.join(__dirname, 'public');


// view engine setup
app.set('views', path.join(__dirname, 'views'));
nunjucks.configure('views', {
  autoescape: true,
  noCache: isDev,
  express: app
});
app.set('view engine', 'html');

// uncomment after placing your favicon in /public
//app.use(favicon(path.join(__dirname, 'public', 'favicon.ico')));
app.use(logger('dev'));


// Default render context
app.use(function(req, res, next) {
  [
    'apiGatewayUrl',
    'discoveryApiUrl',
    'oauthClientId',
    'oauthClientSecret',
    'siteName'
  ].forEach((key) => {
    app.locals[key] = config[key];
  });
  next();
});

app.use('/static', express.static(publicPath));
app.use('/', index);

// catch 404 and forward to error handler
app.use(function(req, res, next) {
  const err = new Error('Not Found');
  err.status = 404;
  next(err);
});

// error handler
app.use(function(err, req, res, next) {
  // set locals, only providing error in development
  res.locals.message = err.message;
  res.locals.error = isDev ? err : {};

  // render the error page
  res.status(err.status || 500);
  res.render('error');
});


module.exports = app;
