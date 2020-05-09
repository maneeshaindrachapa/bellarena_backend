const jwt = require('jsonwebtoken');
const config = require('../../config.json');
const dbConfig = require("../../mysql_connection");
const axios = require('axios');

exports.getItems = function (req, res, next) {
    let query_ = "SELECT * from itemTypes";
    dbConfig.query(query_, (err, rows) => {
        if (err) {
            console.log("Error Connecting to Server !");
            return res.status(404).send({ success: false, message: "Error Connecting to Server!" });
        } else {
            if (rows.length != 0) {
                res.status(200).send({ success: true, data: rows });
            }
        }
    });
};

exports.addFavorites = function (req, res, next) {
    let id = req.body.id;
    let fav = req.body.fav;
    for (let i = 0; i < fav.length; i++) {
        let query_ = "INSERT INTO favoriteitems(userID,itemID) values(?,?)";
        dbConfig.query(query_, [id, fav[i]], (err, rows) => {
            if (err) {
                console.log("Error Connecting to Server !");
                console.log(err);
                return res.status(401).send({ success: false, message: "Error Connecting to Server!" });
            } else {
                console.log("successfully added");
                if (i == fav.length - 1) {
                    let query__ = "UPDATE user set favoritesAdded=? where id=?";
                    dbConfig.query(query__, [1, id], (err, rows) => {
                        if (err) {
                            console.log("Error Connecting to Server !");
                            console.log(err);
                            return res.status(401).send({ success: false, message: "Error Connecting to Server!" });
                        } else {
                            res.status(200).send({ success: true, message: "favorites added successfully" });
                        }
                    });
                }
            }
        });
    }
};

exports.getRecommendedItems = async function (req, res, next) {
    let userID = req.body.id;
    let result = [];
    let clothArray = [];
    const prediction = await axios({
        method: 'post',
        url: 'http://35.226.251.116:5000/predict',
        withCredentials: true,
        crossdomain: true,
        headers: { 'Content-Type': 'application/json' },
        data: { 'user_id': userID },
    }).catch(e => e);
    if (prediction instanceof Error) {
        result = "0";
        console.log('Error E:', prediction)
    } else {
        result = prediction['data']['input_id'];
    }
    for (let i = 0; i < result.length; i++) {
        let query_ = 'SELECT * from cloth where id=?';
        dbConfig.query(query_, [result[i]], (err, rows) => {
            if (err) {
                console.log("Error Connecting to Server !");
                return res.status(404).send({ success: false, message: "Error Connecting to Server!" });
            } else {
                if (rows.length > 0) {
                    clothArray.push(rows);
                }
                if (i == result.length - 1) {
                    res.status(200).send({ success: true, data: clothArray });
                }
            }
        });
    }
};

exports.getReviews = function (req, res, next) {
    let id = req.body.id;
    let query_ = 'SELECT * from ecloths where cloth_id=?';
    dbConfig.query(query_, id, (err, rows) => {
        if (err) {
            console.log("Error Connecting to Server !");
            return res.status(404).send({ success: false, message: "Error Connecting to Server!" });
        } else {
            if (rows.length != 0) {
                res.status(200).send({ success: true, data: rows });
            }
        }
    });
};

exports.addReview = function (req, res, next) {
    let userID = req.body.userID;
    let clothID = req.body.clothID;
    let age =req.body.age;
    let stars = req.body.stars;
    let review = req.body.review;

    let query_ = 'INSERT INTO ecloths(user_id,cloth_id,age,review_text,rating,review_label) values(?,?,?,?,?,?)';
    dbConfig.query(query_, [userID,clothID,age,review,stars,1], (err, rows) => {
        if (err) {
            console.log("Error Connecting to Server !");
            console.log(err);
            return res.status(401).send({ success: false, message: "Error Connecting to Server!" });
        } else {
            res.status(200).send({ success: true, data: {message: "Review successfully Added" } });
        }
    });
}