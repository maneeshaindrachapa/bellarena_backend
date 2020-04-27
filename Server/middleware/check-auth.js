const jwt = require("jsonwebtoken");
const config = require("../../config")

module.exports = function(req, res, next){
    try{

        const decoded = jwt.verify(req.headers.authorization.split(" ")[1], config.env.JWT_KEY);
        req.body.user_data = decoded;
        next();

    }catch (error) {
        return res.status(401).send({success: false, message: "Authentication failed!"});
    }
};