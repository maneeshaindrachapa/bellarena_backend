const jwt = require('jsonwebtoken');
const nodemailer = require('nodemailer');
var smtpTransport = require('nodemailer-smtp-transport');
const config = require('../../config.json');
const dbConfig = require("../../mysql_connection");

exports.register = function (req, res, next) {

    let email = req.body.email;
    let password = req.body.password;
    let firstname = req.body.firstname;
    let lastname = req.body.lastname;
    let address = req.body.address;

    let query_ = "INSERT INTO user(email,password,firstname,lastname,address,favoritesAdded) values(?,?,?,?,?,?)";
    dbConfig.query(query_, [email, password, firstname, lastname, address,0], (err, rows) => {
        if (err) {
            console.log("Error Connecting to Server !");
            console.log(err);
            return res.status(401).send({ success: false, message: "Error Connecting to Server!" });
        } else {
            res.status(200).send({ success: true, data: { email: email, password: password, message: "Account successfully created" } });
        }
    });
};

exports.login = function (req, res, next) {
    let email = req.body.email;
    let password = req.body.password;
    let query_ = "SELECT * from user where email=?";

    dbConfig.query(query_, [email], (err, rows) => {
        if (err) {
            console.log("Error Connecting to Server !");
            return res.status(401).send({ success: false, message: "Error Connecting to Server!" });
        } else {
            try {
                if (rows != null) {
                    if (password == rows[0]['password']) {
                        const token = jwt.sign({
                            user_id: rows[0]["id"],
                            email: rows[0]["email"],
                            password: rows[0]["password"],
                            favoritesAdded :rows[0]['favoritesAdded']
                        },
                            config.env.JWT_KEY,
                            {
                                expiresIn: "2h"
                            });
                        return res.status(200).send({ success: true, message: "Login Successful!", token: token });
                    }
                    else {
                        console.log("Invalid Credentials!");
                        return res.status(401).send({ success: false, message: "Invalid Credentials!" });
                    }
                }
                else {
                    console.log("Invalid Credentials!");
                    return res.status(401).send({ success: false, message: "Invalid Credentials!" });
                }
            } catch (e) {
                console.log(e);
                return res.status(401).send({ success: false, message: "Invalid Credentials!" });
            }

        }
    });
};

exports.forgetPassword = function (req, res, next) {
    let email = req.body.email;
    let query_ = "SELECT * from user where email=?";

    dbConfig.query(query_, [email], (err, rows) => {
        if (err) {
            console.log("Error Connecting to Server !");
            return res.status(404).send({ success: false, message: "Error Connecting to Server!" });
        } else {
            if (rows[0] != null) {
                let randomNo = Math.floor(100000 + Math.random() * 900000);
                let transporter =  nodemailer.createTransport(smtpTransport({
                    service: 'gmail',
                    host: 'smtp.gmail.com',
                    auth: {
                      user: 'snykmonitor95@gmail.com',
                      pass: 'Maneesha@123'
                    }
                  }));
                
                let mailOptions = {
                  from: 'snykmonitor95@gmail.com',
                  to: email,
                  subject: 'Rest Password of Bellarena Account',
                  text: 'Your Six Digit Token:'+randomNo
                };

                let query_0 = "UPDATE user set forgetPasswordNo=? where email=?";
                dbConfig.query(query_0, [randomNo,email], (err, rows) => {
                    if (err) {
                        console.log("Error Connecting to Server !");
                        console.log(err);
                        return res.status(404).send({ success: false, message: "Error Connecting to Server!" });
                    } else {
                        transporter.sendMail(mailOptions, function(error, info){
                            if (error) {
                                return res.status(404).send({ success: false, message: "Error connecting to mail server!" });
                            } else {
                                res.status(200).send({ success: true, data: { email: email, message: "Successfully send the mail" } });
                            }
                          });
                    }
                });
                
            } else {
                console.log("Invalid Email address!");
                return res.status(401).send({ success: false, message: "Invalid Email address!" });
            }
        }
    });
};
exports.changePassword = function(req,res,next){
    let email = req.body.email;
    let password = req.body.password;
    let query_ = "UPDATE user set password=? where email=?";
    dbConfig.query(query_, [password,email], (err, rows) => {
        if (err) {
            console.log("Error Connecting to Server !");
            console.log(err);
            return res.status(401).send({ success: false, message: "Error Connecting to Server!" });
        } else {
            res.status(200).send({ success: true, data: { email: email, password: password, message: "Password Successfully Changed" } });
        }
    });
};
exports.tokenValidation = function(req,res,next){
    let email = req.body.email;
    let token = req.body.token;
    let query_ = "SELECT * from user where email=?";
    dbConfig.query(query_, [email], (err, rows) => {
        if (err) {
            console.log("Error Connecting to Server !");
            return res.status(404).send({ success: false, message: "Error Connecting to Server!" });
        } else {
            if (rows[0] != null) {
                if(rows[0]['forgetPasswordNo'] == token.trim()){
                    res.status(200).send({ success: true, data: { email: email, message: "Valid Token identified !" } });
                }else{
                    return res.status(401).send({ success: false, message: "Invalid token identified !" }); 
                }
            }else{
                console.log("Error Connecting to Server !");
                return res.status(404).send({ success: false, message: "Error Connecting to Server !" }); 
            }
        }
    });
};

exports.get_users = function (req, res, next) {
    let response = {
        count: users.length,
        users: users
    };
    res.status(200).send({ success: true, data: response });
};

exports.delete_user_by_id = function (req, res, next) {

    let user_id = req.params.user_id;
    for (let i = 0; i < users.length; i++) {
        if (users[i]._id == user_id) {

            res.status(200).send({ success: true, message: "User successfully deleted" });
        }
    }

    res.status(404).send({ success: true, message: "No matching users found" });

};

exports.get_user_by_id = function (req, res, next) {

    let user_id = req.params.user_id;
    let user;
    for (let i = 0; i < users.length; i++) {
        if (users[i]._id == user_id) {
            user = users[i];
        }
    }
    if (user) {
        res.status(200).send({ success: true, data: user });
    }
    else {
        res.status(404).send({ success: true, message: "No matching users found" });
    }
};