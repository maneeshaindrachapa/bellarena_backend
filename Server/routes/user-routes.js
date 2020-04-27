const express = require('express');
const router = express.Router();
const userController = require('../Controllers/user-controller');
const check_auth = require("../middleware/check-auth");


router.post('/register', userController.register); 
router.post('/login', userController.login); 
router.post('/forgetpassword',userController.forgetPassword); 
router.post('/forgetpassword/token',userController.tokenValidation); 
router.post('/forgetpassword/changepassword',userController.changePassword); 
router.get('/', check_auth, userController.get_users);
router.delete('/:user_id', check_auth,  userController.delete_user_by_id);
router.get('/:user_id', check_auth,  userController.get_user_by_id); 

module.exports = router;