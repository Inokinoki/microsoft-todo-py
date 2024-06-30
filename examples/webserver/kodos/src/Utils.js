
const AUTH = "auth"

const logout = () => {
    window.localStorage.removeItem(AUTH)
}

const login = (auth_login_res) => {
    window.localStorage.setItem(AUTH, auth_login_res)
}

const getAuth = () => {
    return window.localStorage.getItem(AUTH)
}

export {
    login,
    logout,
    getAuth,
}
