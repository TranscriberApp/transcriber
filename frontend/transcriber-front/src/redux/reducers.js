export const reducer = (state = {}, action) => {
    switch (action.type) {
        case 'LOGIN':
            return Object.assign({}, state, {username: action.username});
        case 'JOIN':
            return Object.assign({}, state, {meeting: action.meeting});
        default:
            return state
    }
};