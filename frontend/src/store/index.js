import { createStore } from "vuex";
import auth from "./modules/auth";

function persistAuthentication(store) {
  const savedState = window.sessionStorage.getItem("workhour-auth");
  if (savedState) {
    try {
      store.replaceState({ ...store.state, auth: JSON.parse(savedState) });
    } catch {
      window.sessionStorage.removeItem("workhour-auth");
    }
  }
  store.subscribe((_mutation, state) => {
    window.sessionStorage.setItem("workhour-auth", JSON.stringify(state.auth));
  });
}

export default createStore({
  modules: {
    auth,
  },
  // Authentication is session-scoped; do not leave bearer tokens in localStorage.
  plugins: [persistAuthentication],
});
