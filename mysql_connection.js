var mysql = require('mysql');

var connection = mysql.createConnection({
  host: "localhost",
  user: "root",
  password: "",
  database: "bellarena"
});

connection.connect(function(err) {
  if (err) throw err;
  console.log("Connected to Bellarena!");
});

module.exports = connection;