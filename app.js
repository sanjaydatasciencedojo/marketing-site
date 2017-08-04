const express = require('express');
const i18n = require('i18n-abide');
const logger = require('morgan');
const nunjucks = require('nunjucks');
const path = require('path');

const index = require('./routes/index');

// Load environment variables from .nev files
// See https://www.npmjs.com/package/dotenv
require('dotenv').config();


const app = express();
const env = app.get('env');
const isDev = env === 'development';
const publicPath = path.join(__dirname, 'public');


// view engine setup
app.set('views', path.join(__dirname, 'views'));
nunjucks.configure('views', {
  autoescape: true,
  noCache: isDev,
  express: app
});
app.set('view engine', 'html');

// Configure internationalization (i18n) for translations and localization

/**
 * Default language locale middleware.
 *
 * This middleware enables the mapping of languages to locale-specific translations. For example, users
 * visiting /es/example will see the page with Spanish (Latin America) [es-419] translations since there are
 * no broad Spanish [es] translations.
 */
app.use(function(req, res, next) {
  const languageMap = {
    en: 'en-US',
    es: 'es-419',
  };

  // Update URL path if language specified on path
  const matches = req.url.match(`^\/(${Object.keys(languageMap).join('|')})(\/|$)`);
  if (matches && matches[1]) {
    req.url = req.url.replace(matches[0], `/${languageMap[matches[1]]}/`);
  }
  next()
});

app.use(i18n.abide({
  supported_languages: ['en-US', 'es-419', 'eo'],
  debug_lang: 'eo',
  default_lang: 'en-US',
  locale_on_url: true,
  translation_directory: 'public/i18n'
}));

/**
 * Add moment to context for date/time formatting.
 */
app.use(function(req, res, next) {
  const moment = require('moment');
  moment.locale(req.locale);
  app.locals.moment = moment;

  next();
});

app.use(logger(isDev ? 'dev' : 'combined'));


// Default render context
app.use(function(req, res, next) {
  [
    'API_GATEWAY_URL',
    'DISCOVERY_API_URL',
    'OAUTH_CLIENT_ID',
    'OAUTH_CLIENT_SECRET',
    'SITE_NAME'
  ].forEach((key) => {
    app.locals[key] = process.env[key];
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
