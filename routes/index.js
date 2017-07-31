const DiscoveryService = require('../services/discovery');
const express = require('express');
const router = express.Router();

router.get('/:programType(micromasters|professional-certificate|xseries)/:marketingSlug([\\w-]+)',
  function(req, res, next) {
    // TODO Catch not found errors, and render the 404 page.
    const locals = req.app.locals;
    const discoveryService = new DiscoveryService(
      locals.apiGatewayUrl,
      locals.oauthClientId,
      locals.oauthClientSecret,
      locals.discoveryApiUrl
    );
    discoveryService.getProgram(req.params.programType, req.params.marketingSlug)
      .then((programData) => {
        res.render('program-detail', {title: programData.title, program: programData});
      })
      .catch((err) => {
        // TODO Raise error
        console.error(err);
        res.status(500).send('Something broke!');
      });
  }
);

module.exports = router;
