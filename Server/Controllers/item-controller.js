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

exports.addFavorites = function(req,res,next){
    let id = req.body.id;
    let fav = req.body.fav;
    for(let i=0;i<fav.length;i++){
        let query_ = "INSERT INTO favoriteitems(userID,itemID) values(?,?)";
        dbConfig.query(query_, [id,fav[i]], (err, rows) => {
            if (err) {
                console.log("Error Connecting to Server !");
                console.log(err);
                return res.status(401).send({ success: false, message: "Error Connecting to Server!" });
            } else {
                console.log("successfully added");
                if(i==fav.length-1){
                    let query__="UPDATE user set favoritesAdded=? where id=?";
                    dbConfig.query(query__, [1,id], (err, rows) => {
                        if (err) {
                            console.log("Error Connecting to Server !");
                            console.log(err);
                            return res.status(401).send({ success: false, message: "Error Connecting to Server!" });
                        } else {
                            res.status(200).send({ success: true, message: "favorites added successfully"});
                        }
                    });
                }
            }
        });
    }
};