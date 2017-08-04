// Invalidates CloudFront paths.
// Use after deployment to ensure users see the latest version of the application.
// NOTE: The user running this script must have access to CloudFront to create an invalidation.
// See https://aws.amazon.com/sdk-for-node-js/ for info on credentials.

require('dotenv').config();
const assert = require('assert');
const AWS = require('aws-sdk');
const CloudFront = new AWS.CloudFront();
const crypto = require('crypto');

const cloudFrontDistributionId = process.env.CLOUDFRONT_DISTRIBUTION_ID;
assert(cloudFrontDistributionId, 'No CloudFront distribution ID provided!');

const paths = [
  '/bio/*',
  '/micromasters/*',
  '/professional-certificate/*',
  '/xseries/*',
];
const params = {
  DistributionId: cloudFrontDistributionId,
  InvalidationBatch: {
    CallerReference: crypto.randomBytes(4).toString('hex'),
    Paths: {
      Quantity: paths.length,
      Items: paths
    }
  }
};

CloudFront.createInvalidation(params, function(err, data) {
  if (err) {
    console.log(err, err.stack);
  }
  else {
    console.log(data);
  }
});
