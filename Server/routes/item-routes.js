const express = require('express');
const router = express.Router();
const itemController = require('../Controllers/item-controller');
const check_auth = require("../middleware/check-auth");


router.get('/', itemController.getItems); 
router.post('/favorite',itemController.addFavorites);

module.exports = router;