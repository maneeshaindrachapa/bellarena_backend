const jwt = require('jsonwebtoken');
const config = require('../../config.json');
const dbConfig = require("../../mysql_connection");

exports.getItems = function (req, res, next) {
    let query_ = "SELECT * from itemTypes";
    dbConfig.query(query_,  (err, rows) => {
        if (err) {
            console.log("Error Connecting to Server !");
            return res.status(404).send({ success: false, message: "Error Connecting to Server!" });
        } else {
            if(rows.length!=0){
                res.status(200).send({ success: true, data: rows});
            }
         }
    });
};