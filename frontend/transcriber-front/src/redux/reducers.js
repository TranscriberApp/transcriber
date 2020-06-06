const initialState = {
  participants: [],
  messages: [{
    author: "ChatBot",
    msg: "Welcome!"
  }],
  username: undefined,
  meeting: undefined,
  isHost: false,
};

export const reducer = (state = initialState, action) => {
  switch (action.type) {
    case "LOGIN":
      return Object.assign({}, state, { username: action.username });
    case "JOIN":
      return Object.assign({}, state, { meeting: action.meeting });
    case "CREATE":
      return Object.assign({}, state, {
        meeting: action.meeting,
        isHost: true,
      });
    case "SET_PARTICIPANTS_LIST":
      return Object.assign({}, state, { participants: action.participants });
    case "RECEIVED_MESSAGE":
      return Object.assign({}, state, {
        messages: state.messages.concat({msg: action.msg, author: action.username}),
      });
    default:
      return state;
  }
};
