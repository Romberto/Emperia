import React from "react";
import styled from "./Header.module.css";
import logo from "../../../assets/moto.png";
import TelegramLoginButton from "../TelegramButton/TelegramButton";
import axios from 'axios';

type UserTelegramType = {
  id: number;
  first_name?: string;
  last_name?: string;
  username?: string;
  auth_date: number;
  hash: string;
};

export const Header: React.FC = () => {
  const handleTelegramAuth = async (user: UserTelegramType) => {
    
  };
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
        <TelegramLoginButton
          botName="SimplyMenuBot"
          onAuth={handleTelegramAuth}
        />
      </div>
    </header>
  );
};
