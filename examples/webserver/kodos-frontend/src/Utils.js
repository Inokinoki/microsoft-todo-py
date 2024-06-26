
const AUTH = "auth"

const logout = () => {
    window.localStorage.removeItem(AUTH)
}

const login = (auth_login_res) => {
    window.localStorage.setItem(AUTH, auth_login_res)
}

export {
    login,
    logout,
}
