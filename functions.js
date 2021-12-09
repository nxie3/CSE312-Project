function submit_form(){
    const password_element = document.getElementById("passwordInput");
    const password = password_element.value

    if ((password.length >= 8) && (contains_Special(password)) && (contains_Number(password)) && (password.toUpperCase() !== password) && (password.toLowerCase() !== password)){
        const json = parse_doc();

        const request = new XMLHttpRequest();
        request.onreadystatechange = function (){
            if(this.readyState === 4 && this.status === 200){
                console.log(this.responseText)
            }
        }

        request.open("POST", "/registered");
        request.send(json);
        alert("Registered! Please go log in!")
    }else{
        alert("Invalid Password!")
    }
}

function contains_Special(password){
    for (let i = 0; i < password.length; i++){
        if (password.codePointAt(i) >= 32 || password.codePointAt(i) <= 47){
            return true
        }else if (password.codePointAt(i) >= 58 || password.codePointAt(i) <= 64){
            return true
        }else if (password.codePointAt(i) >= 91 || password.codePointAt(i) <= 96){
            return true
        }else if (password.codePointAt(i) >= 123 || password.codePointAt(i) <= 126){
            return true
        }
    }
    return false
}

function contains_Number(password){
    return /\d/.test(password)
}

function login_form(){
    const json = parse_login()

    const request = new XMLHttpRequest();
    request.onreadystatechange = function (){
        if(this.readyState === 4 && this.status === 200){
            console.log(this.responseText)
        }
    }

    request.open("POST", "/logged");
    request.send(json);
}

function parse_login(){
    const username_element = document.getElementById("username");
    const password_element = document.getElementById("password");

    const username = username_element.value
    const password = password_element.value

    username_element.value = ""
    password_element.value = ""

    const login_info = {username: username, password: password}

    return JSON.stringify(login_info)
}

function parse_doc(){
    const username_element = document.getElementById("usernameInput");
    const password_element = document.getElementById("passwordInput");

    const username = username_element.value
    const password = password_element.value

    username_element.value = ""
    password_element.value = ""

    const registration = {username: username, password: password}

    return JSON.stringify(registration)
}