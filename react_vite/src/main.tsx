import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { HashRouter  } from "react-router";
import "./index.css";
import App from "./App.tsx";
import { Provider } from "react-redux";
import { store } from "./app/store.ts";

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <HashRouter>
      <Provider store={store}>
        <App />
      </Provider>
      
    </HashRouter>
  </StrictMode>
);
