import "./App.css";
import { Routes, Route } from "react-router";
import { Header } from "./components/UI/Header/Header";
import { Home } from "./components/page/Home";
import { Festivals } from "./components/page/Festivals";
import { HelpPage } from "./components/page/HelpPage";
import { Servisec } from "./components/page/Servisec";
import { Sos } from "./components/page/Sos";
import { Sales } from "./components/page/Sales";

function App() {
  return (
    <>
      <div className="base">
        <div className="container">
          <Header />
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/festivals" element={<Festivals />} />
            <Route path="/help" element={<HelpPage />} />
            <Route path="/servisec" element={<Servisec />} />
            <Route path="/sales" element={<Sales />}></Route>
            <Route path={"/sos"} element={<Sos />}></Route>
          </Routes>
        </div>
      </div>
    </>
  );
}

export default App;
