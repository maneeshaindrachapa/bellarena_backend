const express = require('express');
const router = express.Router();
const itemController = require('../Controllers/item-controller');
const check_auth = require("../middleware/check-auth");


router.get('/', itemController.getItems); 
router.post('/favorite',itemController.addFavorites);
router.post('/recommend',itemController.getRecommendedItems);
router.post('/reviews',itemController.getReviews);
router.post('/addReview',itemController.addReview);

module.exports = router;