var ghpages = require("gh-pages");
ghpages.publish(".",{ src : ["build/*", "data/*", "index.html", ".nojekyll"] }, function(error){
    if (error) {
        console.log("ERROR", error);
    }
    else {
        console.log("Build");
    }
})