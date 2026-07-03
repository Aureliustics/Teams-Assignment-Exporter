/*
This is used for the getting your authentication token to allow the API to work. You can also get the token by going into developer tools -> network tab ->
filter by graph.microsoft.com -> open any assignment -> copying Authorization token under Request Headers (make sure you dont copy the "Bearer" part)
Copy paste this into developer tools (F12) after opening an assignment to print out your token.
You might need to write "allow pasting" before teams allows you to paste the script.
*/


function fetchToken(){
    const keys = Object.keys(localStorage);

    const foundTokens = [];

    for (const key of keys){
        const data = localStorage.getItem(key);
        let verifyData;
        
        try {
            verifyData = JSON.parse(data);
        }
        catch {
            continue;//if not json then skip
        }

        if (verifyData?.credentialType?.toLowerCase() == "accesstoken" && verifyData?.target?.includes("graph.microsoft.com")){
            foundTokens.push(verifyData);
        }
    }

    return foundTokens;
}

const fetchedTokens = fetchToken();

if (fetchedTokens.length == 0){
    console.log("No tokens found, try opening an assignment before running this script.");
}
else {
    const foundToken = fetchedTokens[0].secret;
    console.log(`Token found. Copy and paste this into teams exporter:\n\n${foundToken}`);
}

