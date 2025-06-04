import React from "react";
import styled from "./Header.module.css";
import { Button } from "../Button/Button";
import logo from "../../../assets/moto.png";

export const Header: React.FC = () => {
  return (
    <header>
      <a href="#">
        <img
          className={styled.logo__img}
          src={logo}
          alt="логотип клуба в виде английских букв I, а так же W"
        />
      </a>
      <div className={styled.auth}>
        <Button variant="green">Воити</Button>
        <Button variant="green">Зарегистрироваться</Button>
      </div>
    </header>
  );
};
