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